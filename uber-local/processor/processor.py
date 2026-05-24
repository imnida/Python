"""
Layers 2 + 3 + 4 – Stream Processor
Consumes the Redis Stream and fans out to three destinations:
  • Ring Buffer  (Redis List, last 5 positions per driver)   → serves the rider map
  • H3 Spatial Index (Redis Sets keyed by hex cell)          → serves the dispatch engine
  • SQLite        (durable, time-range queryable storage)    → serves analytics
"""

import asyncio
import json
import os
import sqlite3
import time

import h3
import redis.asyncio as aioredis

REDIS_HOST      = os.getenv("REDIS_HOST", "localhost")
DB_PATH         = os.getenv("DB_PATH", "/data/gps.db")
BATCH_SIZE      = int(os.getenv("BATCH_SIZE", "100"))
STREAM_KEY      = "gps:stream"
CONSUMER_GROUP  = "processors"
CONSUMER_NAME   = "processor-1"
RING_BUFFER_LEN = 5     # keep last N positions per driver in Redis
DRIVER_TTL_S    = 120   # remove driver from indexes after 2 min silence


# ── SQLite setup ──────────────────────────────────────────────────────────────

def init_db(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.executescript("""
        PRAGMA journal_mode = WAL;
        PRAGMA synchronous  = NORMAL;
        PRAGMA cache_size   = -32000;

        CREATE TABLE IF NOT EXISTS gps_pings (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            driver_id   TEXT    NOT NULL,
            lat         REAL    NOT NULL,
            lng         REAL    NOT NULL,
            timestamp   REAL    NOT NULL,
            speed       REAL    DEFAULT 0,
            bearing     REAL    DEFAULT 0,
            status      TEXT    DEFAULT 'available',
            h3_cell     TEXT,
            ingested_at REAL    DEFAULT (unixepoch('now', 'subsec'))
        );
        CREATE INDEX IF NOT EXISTS idx_driver_time ON gps_pings(driver_id, timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_h3_time     ON gps_pings(h3_cell, timestamp DESC);
    """)
    conn.commit()
    return conn


def flush_batch(conn: sqlite3.Connection, batch: list):
    if not batch:
        return
    conn.executemany(
        "INSERT INTO gps_pings "
        "(driver_id, lat, lng, timestamp, speed, bearing, status, h3_cell) "
        "VALUES (?,?,?,?,?,?,?,?)",
        batch,
    )
    conn.commit()


# ── Redis fan-out ─────────────────────────────────────────────────────────────

async def process_message(r: aioredis.Redis, data: dict) -> tuple:
    """Update ring buffer + spatial index in Redis. Returns a DB row tuple."""
    driver_id = data["driver_id"]
    lat       = float(data["lat"])
    lng       = float(data["lng"])
    ts        = float(data["timestamp"])
    speed     = float(data.get("speed", 0))
    bearing   = float(data.get("bearing", 0))
    status    = data.get("status", "available")
    h3_cell   = data.get("h3_cell") or h3.geo_to_h3(lat, lng, 8)

    position_json = json.dumps(
        {"lat": lat, "lng": lng, "ts": ts,
         "speed": speed, "bearing": bearing, "status": status}
    )

    pipe = r.pipeline(transaction=False)

    # ── Ring Buffer (Layer 3) ─────────────────────────────────────────
    ring_key = f"driver:{driver_id}:ring"
    pipe.lpush(ring_key, position_json)
    pipe.ltrim(ring_key, 0, RING_BUFFER_LEN - 1)
    pipe.expire(ring_key, DRIVER_TTL_S)

    # ── Current position (fast point-lookup for map rendering) ────────
    cur_key = f"driver:{driver_id}:cur"
    pipe.hset(cur_key, mapping={
        "lat": lat, "lng": lng, "ts": ts,
        "speed": speed, "bearing": bearing,
        "status": status, "h3_cell": h3_cell,
    })
    pipe.expire(cur_key, DRIVER_TTL_S)

    # ── H3 Spatial Index (Layer 2 routing, used by dispatch) ─────────
    old_cell = await r.get(f"driver:{driver_id}:h3")
    if old_cell and old_cell != h3_cell:
        pipe.srem(f"h3:{old_cell}:drivers", driver_id)
    pipe.sadd(f"h3:{h3_cell}:drivers", driver_id)
    pipe.expire(f"h3:{h3_cell}:drivers", DRIVER_TTL_S)
    pipe.set(f"driver:{driver_id}:h3", h3_cell, ex=DRIVER_TTL_S)

    # ── Available driver global set (for stats) ───────────────────────
    if status == "available":
        pipe.sadd("drivers:available", driver_id)
    else:
        pipe.srem("drivers:available", driver_id)

    await pipe.execute()

    return (driver_id, lat, lng, ts, speed, bearing, status, h3_cell)


# ── Main loop ─────────────────────────────────────────────────────────────────

async def main():
    r = aioredis.from_url(f"redis://{REDIS_HOST}:6379", decode_responses=True)
    conn = init_db(DB_PATH)

    try:
        await r.xgroup_create(STREAM_KEY, CONSUMER_GROUP, id="0", mkstream=True)
        print(f"Created consumer group '{CONSUMER_GROUP}'")
    except Exception:
        print(f"Consumer group '{CONSUMER_GROUP}' already exists")

    print(f"Processor ready — batch_size={BATCH_SIZE}")

    db_batch: list = []
    last_flush = time.monotonic()

    while True:
        messages = await r.xreadgroup(
            CONSUMER_GROUP,
            CONSUMER_NAME,
            {STREAM_KEY: ">"},
            count=BATCH_SIZE,
            block=200,
        )

        if not messages:
            # Flush any pending DB batch on idle
            if db_batch:
                flush_batch(conn, db_batch)
                db_batch.clear()
                last_flush = time.monotonic()
            continue

        _, entries = messages[0]
        msg_ids = []

        for msg_id, data in entries:
            row = await process_message(r, data)
            db_batch.append(row)
            msg_ids.append(msg_id)

        # Acknowledge stream messages
        await r.xack(STREAM_KEY, CONSUMER_GROUP, *msg_ids)

        # Flush DB batch when full or every 500 ms
        now = time.monotonic()
        if len(db_batch) >= BATCH_SIZE or (now - last_flush) >= 0.5:
            flush_batch(conn, db_batch)
            count = len(db_batch)
            db_batch.clear()
            last_flush = now
            print(f"Flushed {count} rows to SQLite | stream acked {len(msg_ids)}")


if __name__ == "__main__":
    asyncio.run(main())

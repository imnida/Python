"""
Layer 1 – Ingestion Edge
Validates, deduplicates and rate-limits every GPS ping before anything
downstream ever sees it.  Publishes accepted pings to Redis Streams.
"""

import os
import time
from typing import Optional

import h3
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
STREAM_KEY = "gps:stream"
STREAM_MAXLEN = 500_000   # ~5 minutes of data at 2 000 pings/s
STALE_WINDOW_S = 30       # reject pings older than 30 s

app = FastAPI(title="Ingestion Edge")
redis_client: aioredis.Redis = None

# Lua script: allow at most 1 ping per driver per second (rate-limit)
_RATE_LIMIT_LUA = """
local key   = KEYS[1]
local now   = tonumber(ARGV[1])
local last  = tonumber(redis.call('GET', key) or 0)
if (now - last) < 1.0 then return 0 end
redis.call('SET', key, ARGV[1], 'EX', 5)
return 1
"""


@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = aioredis.from_url(
        f"redis://{REDIS_HOST}:6379", decode_responses=True
    )


class GPSPing(BaseModel):
    driver_id: str
    lat: float
    lng: float
    timestamp: Optional[float] = None
    speed: float = 0.0
    bearing: float = 0.0
    status: str = "available"   # available | busy | offline

    @field_validator("lat")
    @classmethod
    def check_lat(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("latitude out of range")
        return round(v, 6)

    @field_validator("lng")
    @classmethod
    def check_lng(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("longitude out of range")
        return round(v, 6)

    @field_validator("status")
    @classmethod
    def check_status(cls, v):
        if v not in {"available", "busy", "offline"}:
            raise ValueError("invalid status")
        return v


@app.post("/ping", status_code=202)
async def receive_ping(ping: GPSPing):
    now = time.time()

    # ── 1. Timestamp validation (reject stale / future pings) ──────────
    if ping.timestamp is None:
        ping.timestamp = now
    elif abs(ping.timestamp - now) > STALE_WINDOW_S:
        raise HTTPException(400, "Stale ping rejected")

    # ── 2. Rate limiting (1 ping / driver / second) ────────────────────
    allowed = await redis_client.eval(
        _RATE_LIMIT_LUA, 1, f"rate:{ping.driver_id}", str(now)
    )
    if not allowed:
        raise HTTPException(429, "Rate limit: 1 ping/s per driver")

    # ── 3. Compute H3 cell (resolution 8 ≈ 460 m hexagons) ────────────
    h3_cell = h3.geo_to_h3(ping.lat, ping.lng, 8)

    # ── 4. Publish to Redis Stream ─────────────────────────────────────
    await redis_client.xadd(
        STREAM_KEY,
        {
            "driver_id": ping.driver_id,
            "lat": str(ping.lat),
            "lng": str(ping.lng),
            "timestamp": str(ping.timestamp),
            "speed": str(ping.speed),
            "bearing": str(ping.bearing),
            "status": ping.status,
            "h3_cell": h3_cell,
        },
        maxlen=STREAM_MAXLEN,
        approximate=True,
    )

    return {"status": "accepted", "h3_cell": h3_cell}


@app.get("/health")
async def health():
    stream_len = await redis_client.xlen(STREAM_KEY)
    return {"status": "ok", "stream_length": stream_len}

"""
Layer 5 – Dispatch Engine
Uses the H3 spatial index built by the processor to find the nearest
available drivers in under 100 ms.
"""

import math
import os
import sqlite3
from typing import List, Optional

import h3
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException, Query

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
DB_PATH    = os.getenv("DB_PATH", "/data/gps.db")

# H3 resolution 8: each hexagon is ~460 m across.
# k=1 covers 1 ring (7 cells ≈ 1.4 km radius).
H3_RES          = 8
KM_PER_RING     = 0.46 * 1.5   # approximate

app = FastAPI(title="Dispatch Engine")
redis_client: aioredis.Redis = None


@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = aioredis.from_url(
        f"redis://{REDIS_HOST}:6379", decode_responses=True
    )


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1))
         * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return R * 2 * math.asin(math.sqrt(a))


@app.get("/drivers/nearby")
async def find_nearby_drivers(
    lat: float = Query(..., description="Pickup latitude"),
    lng: float = Query(..., description="Pickup longitude"),
    radius_km: float = Query(5.0, ge=0.1, le=50.0, description="Search radius km"),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Find available drivers near a pickup point.
    Uses the H3 ring-disk to collect candidate cells, then filters by
    exact Haversine distance.  Typical latency: < 5 ms.
    """
    k = max(1, round(radius_km / KM_PER_RING))
    pickup_cell  = h3.geo_to_h3(lat, lng, H3_RES)
    search_cells = h3.k_ring(pickup_cell, k)

    # Fetch driver sets for all candidate cells in one pipeline
    pipe = redis_client.pipeline(transaction=False)
    for cell in search_cells:
        pipe.smembers(f"h3:{cell}:drivers")
    cell_results = await pipe.execute()

    candidate_ids: set[str] = set()
    for members in cell_results:
        candidate_ids.update(members)

    if not candidate_ids:
        return {"drivers": [], "count": 0, "cells_searched": len(search_cells)}

    # Fetch current positions for candidates (pipeline)
    candidates = list(candidate_ids)[: limit * 5]
    pipe = redis_client.pipeline(transaction=False)
    for did in candidates:
        pipe.hgetall(f"driver:{did}:cur")
    positions = await pipe.execute()

    nearby = []
    for driver_id, pos in zip(candidates, positions):
        if not pos or pos.get("status") != "available":
            continue
        dist = haversine_km(lat, lng, float(pos["lat"]), float(pos["lng"]))
        if dist > radius_km:
            continue
        nearby.append({
            "driver_id": driver_id,
            "lat":        float(pos["lat"]),
            "lng":        float(pos["lng"]),
            "distance_km": round(dist, 3),
            "eta_min":     round(dist / 0.5, 1),   # assumes ~30 km/h
            "speed":       float(pos.get("speed", 0)),
            "bearing":     float(pos.get("bearing", 0)),
        })

    nearby.sort(key=lambda x: x["distance_km"])
    return {
        "drivers":       nearby[:limit],
        "count":         len(nearby),
        "cells_searched": len(search_cells),
    }


@app.get("/drivers/{driver_id}/ring")
async def get_driver_ring_buffer(driver_id: str):
    """Return the last 5 positions from the in-memory ring buffer."""
    raw = await redis_client.lrange(f"driver:{driver_id}:ring", 0, -1)
    if not raw:
        raise HTTPException(404, "Driver not found or offline")
    import json
    return {"driver_id": driver_id, "positions": [json.loads(p) for p in raw]}


@app.get("/drivers/{driver_id}/history")
async def get_driver_history(
    driver_id: str,
    limit: int = Query(200, ge=1, le=10_000),
):
    """Return historical GPS pings from durable SQLite storage."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT lat, lng, timestamp, speed, bearing, status, h3_cell "
        "FROM gps_pings WHERE driver_id=? ORDER BY timestamp DESC LIMIT ?",
        (driver_id, limit),
    ).fetchall()
    conn.close()
    if not rows:
        raise HTTPException(404, "No history for driver")
    return {"driver_id": driver_id, "positions": [dict(r) for r in rows]}


@app.get("/stats")
async def stats():
    available = await redis_client.scard("drivers:available")
    stream_len = await redis_client.xlen("gps:stream")
    return {
        "available_drivers": available,
        "stream_backlog":    stream_len,
    }


@app.get("/health")
async def health():
    return {"status": "ok"}

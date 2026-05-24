"""
Layer 6 – Map Rendering Backend
Serves the Leaflet.js dashboard and pushes live driver positions via
WebSocket, batching stream messages to avoid overwhelming the browser.
"""

import asyncio
import json
import os
from pathlib import Path

import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
STREAM_KEY = "gps:stream"
WS_BATCH_INTERVAL = 0.1   # push to browser at most every 100 ms

app = FastAPI(title="Uber Dashboard")
redis_client: aioredis.Redis = None
STATIC_DIR = Path(__file__).parent / "static"


@app.on_event("startup")
async def startup():
    global redis_client
    redis_client = aioredis.from_url(
        f"redis://{REDIS_HOST}:6379", decode_responses=True
    )


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/config.js")
async def config_js():
    """Expose server-side env vars to the browser."""
    center_lat = os.getenv("CENTER_LAT", "48.8566")
    center_lng = os.getenv("CENTER_LNG", "2.3522")
    from fastapi.responses import Response
    js = f"window.MAP_CENTER = [{center_lat}, {center_lng}];\n"
    return Response(content=js, media_type="application/javascript")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    last_id = "$"
    buffer: list[dict] = []
    last_push = asyncio.get_event_loop().time()

    try:
        while True:
            messages = await redis_client.xread(
                {STREAM_KEY: last_id}, count=200, block=50
            )

            if messages:
                _, entries = messages[0]
                last_id = entries[-1][0]
                for _, data in entries:
                    buffer.append({
                        "driver_id": data["driver_id"],
                        "lat":       float(data["lat"]),
                        "lng":       float(data["lng"]),
                        "bearing":   float(data.get("bearing", 0)),
                        "status":    data.get("status", "available"),
                    })

            now = asyncio.get_event_loop().time()
            if buffer and (now - last_push) >= WS_BATCH_INTERVAL:
                await websocket.send_text(json.dumps(buffer))
                buffer.clear()
                last_push = now

    except WebSocketDisconnect:
        pass
    except Exception:
        pass


app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

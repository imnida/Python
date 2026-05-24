"""
Driver Simulator
Generates realistic GPS pings for N virtual drivers moving around a city.
Each driver follows a random walk, bounces back when it drifts too far from
the city center, and sends exactly 1 ping/second to the ingestion edge.
"""

import asyncio
import math
import os
import random
import time

import aiohttp

INGESTION_URL = os.getenv("INGESTION_URL", "http://localhost:8001")
NUM_DRIVERS   = int(os.getenv("NUM_DRIVERS", "200"))
CENTER_LAT    = float(os.getenv("CENTER_LAT", "48.8566"))
CENTER_LNG    = float(os.getenv("CENTER_LNG", "2.3522"))
MAX_RADIUS_KM = 12.0    # drivers stay within this radius of center


class Driver:
    def __init__(self, driver_id: str):
        self.driver_id = driver_id
        angle = random.uniform(0, 2 * math.pi)
        r     = random.uniform(0, MAX_RADIUS_KM * 0.5)
        self.lat     = CENTER_LAT + (r / 111.0) * math.cos(angle)
        self.lng     = CENTER_LNG + (r / (111.0 * math.cos(math.radians(CENTER_LAT)))) * math.sin(angle)
        self.speed   = random.uniform(15, 55)   # km/h
        self.bearing = random.uniform(0, 360)
        self.status  = "available" if random.random() > 0.25 else "busy"
        self._dir_timer = random.uniform(0, 20)

    def step(self, dt: float = 1.0) -> dict:
        self._dir_timer -= dt
        if self._dir_timer <= 0:
            self.bearing += random.uniform(-60, 60)
            self.bearing %= 360
            self.speed = max(5.0, min(80.0, self.speed + random.uniform(-8, 8)))
            self._dir_timer = random.uniform(8, 30)
            # Occasionally change status
            if random.random() < 0.02:
                self.status = "busy" if self.status == "available" else "available"

        dist_km = self.speed * dt / 3600.0
        rad     = math.radians(self.bearing)
        self.lat += (dist_km / 111.0) * math.cos(rad)
        self.lng += (dist_km / (111.0 * math.cos(math.radians(self.lat)))) * math.sin(rad)

        # Turn back toward center when too far
        dist_from_center = math.sqrt(
            ((self.lat - CENTER_LAT) * 111.0) ** 2
            + ((self.lng - CENTER_LNG) * 111.0 * math.cos(math.radians(self.lat))) ** 2
        )
        if dist_from_center > MAX_RADIUS_KM:
            self.bearing = math.degrees(
                math.atan2(CENTER_LNG - self.lng, CENTER_LAT - self.lat)
            ) % 360
            self.speed = max(self.speed, 30.0)

        return {
            "driver_id": self.driver_id,
            "lat":       round(self.lat, 6),
            "lng":       round(self.lng, 6),
            "speed":     round(self.speed, 1),
            "bearing":   round(self.bearing, 1),
            "timestamp": time.time(),
            "status":    self.status,
        }


async def send_ping(
    session: aiohttp.ClientSession,
    driver: Driver,
    sem: asyncio.Semaphore,
):
    async with sem:
        payload = driver.step()
        try:
            async with session.post(
                f"{INGESTION_URL}/ping",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=3),
            ) as resp:
                if resp.status not in (200, 202, 429):
                    pass  # ignore validation errors from the edge
        except Exception:
            pass  # never let a single driver failure stop the simulation


async def main():
    drivers = [Driver(f"drv-{i:04d}") for i in range(NUM_DRIVERS)]
    sem     = asyncio.Semaphore(80)   # max concurrent HTTP requests

    print(f"Simulator started: {NUM_DRIVERS} drivers centred on "
          f"{CENTER_LAT:.4f}, {CENTER_LNG:.4f}")

    async with aiohttp.ClientSession() as session:
        tick = 0
        while True:
            t0    = time.monotonic()
            tasks = [send_ping(session, d, sem) for d in drivers]
            await asyncio.gather(*tasks)
            elapsed = time.monotonic() - t0
            tick   += 1
            if tick % 10 == 0:
                print(f"tick={tick} | {NUM_DRIVERS} pings in {elapsed:.3f}s")
            await asyncio.sleep(max(0.0, 1.0 - elapsed))


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
from collections.abc import AsyncGenerator
import httpx                              

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import Context, RunYield, RunYieldResume, Server

server = Server()

async def get_london_weather() -> str:
    """Fetch current London weather from the free Open‑Meteo API."""
    params = {
        "latitude": 51.5072,          # London coordinates
        "longitude": -0.1276,
        "current_weather": True,
        "timezone": "Europe/London"
    }
    url = "https://api.open-meteo.com/v1/forecast"

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        cw = resp.json()["current_weather"]

    return (
        f"Weather in London: {cw['temperature']} °C, "
        f"wind {cw['windspeed']} km/h, code {cw['weathercode']}."
    )

@server.agent()
async def london_weather_agent(
    input: list[Message], context: Context
) -> AsyncGenerator[RunYield, RunYieldResume]:
    """Returns current London weather."""
    for _ in input:
        yield {"thought": "Fetching London weather…"}
        weather = await get_london_weather()
        yield Message(
            role="agent",
            parts=[MessagePart(content=weather, content_type="text/plain")]
        )

server.run()
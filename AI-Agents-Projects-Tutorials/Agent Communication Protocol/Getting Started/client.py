import asyncio

from acp_sdk.client import Client
from acp_sdk.models import Message, MessagePart


async def call_london_weather_agent() -> None:
    async with Client(base_url="http://localhost:8000") as client:
        run = await client.run_sync(
            agent="london_weather_agent",
            input=[
                Message(
                    parts=[MessagePart(content="Tell me the weather", content_type="text/plain")]
                )
            ],
        )

        print("Response from london_weather_agent:")
        for message in run.output:
            for part in message.parts:
                print("-", part.content)


if __name__ == "__main__":
    asyncio.run(call_london_weather_agent())

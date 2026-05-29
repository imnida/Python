import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest
import asyncio
import uuid


BASE_URL = "http://localhost:5001"


async def main():
    async with httpx.AsyncClient() as httpx_client:
        # Resolve the agent card
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=BASE_URL,
        )

        # Get the agent card
        agent_card = await resolver.get_agent_card()
        print(f"Connected to agent: {agent_card.name}")
        print(f"Description: {agent_card.description}")
        print()

        # Create client
        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=agent_card,
        )

        # Send a task
        task_description = "Generate a random number between 1 and 100"
        print(f"Sending task: {task_description}")

        request = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(
                message={
                    "role": "user",
                    "parts": [{"text": task_description}],
                    "messageId": str(uuid.uuid4()),
                }
            ),
        )

        response = await client.send_message(request)
        print(f"Response: {response}")


if __name__ == "__main__":
    asyncio.run(main())

import random
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    UnsupportedOperationError,
)
from a2a.utils import new_agent_text_message


class RandomNumberAgent:
    """Agent that generates random numbers."""

    async def invoke(self, query: str) -> str:
        # Default range
        min_val, max_val = 1, 100

        # Try to parse range from query
        words = query.lower().split()
        for i, word in enumerate(words):
            if word == 'between' and i + 3 < len(words):
                try:
                    min_val = int(words[i + 1])
                    max_val = int(words[i + 3])
                except ValueError:
                    pass

        result = random.randint(min_val, max_val)
        return f"Random number between {min_val} and {max_val}: {result}"


class RandomNumberAgentExecutor(AgentExecutor):
    """Executor for the RandomNumberAgent."""

    def __init__(self):
        self.agent = RandomNumberAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        result = await self.agent.invoke(context.get_user_input())
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise UnsupportedOperationError()

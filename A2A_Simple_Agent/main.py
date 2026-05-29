import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from agent_executor import RandomNumberAgentExecutor


def create_app():
    capabilities = AgentCapabilities(streaming=False)

    skill = AgentSkill(
        id="random_number",
        name="Random Number Generator",
        description="Generates random numbers within a specified range",
        inputModes=["text"],
        outputModes=["text"],
    )

    agent_card = AgentCard(
        name="Random Number Agent",
        description="An agent that generates random numbers",
        url="http://localhost:5001/",
        version="1.0.0",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        capabilities=capabilities,
        skills=[skill],
    )

    request_handler = DefaultRequestHandler(
        agent_executor=RandomNumberAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    return A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5001, reload=True)

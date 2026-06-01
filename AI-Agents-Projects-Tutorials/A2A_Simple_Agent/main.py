import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill
from agent_executor import RandomNumberAgentExecutor


def main():
    # Define the skill metadata
    skill = AgentSkill(
        id="random_number",
        name="Random Number Generator",
        description="Generates a random number between 1 and 100",
        tags=["random", "number", "utility"],
        examples=["Give me a random number", "Roll a number", "Random"],
    )

    # Define the agent metadata
    agent_card = AgentCard(
        name="Random Number Agent",
        description="An agent that returns a random number between 1 and 100",
        url="http://localhost:9999/",
        defaultInputModes=["text"],
        defaultOutputModes=["text"],
        skills=[skill],
        version="1.0.0",
        capabilities=AgentCapabilities(),
    )

    # Configure the request handler with our custom agent executor
    request_handler = DefaultRequestHandler(
        agent_executor=RandomNumberAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    # Create the A2A app server
    server = A2AStarletteApplication(
        http_handler=request_handler,
        agent_card=agent_card,
    )

    # Run the server
    uvicorn.run(server.build(), host="0.0.0.0", port=9999)


if __name__ == "__main__":
    main()

# 🤖 A2A Simple Agent Example
This repo demonstrates a minimal A2A (Agent-to-Agent) agent implementation using Google's a2a-sdk and python-a2a libraries. The agent is a simple Random Number Generator that receives tasks from a client and responds with random numbers.

## Features
- **A2A Protocol**: Implements the Agent-to-Agent communication protocol
- **Random Number Generation**: Simple agent that generates random numbers within a specified range
- **FastAPI Backend**: Uses Starlette/Uvicorn for the HTTP server
- **Client Support**: Includes a client script to send tasks to the agent

## Setup

### Prerequisites
- Python 3.13+
- uv (Python package manager)

### Installation
```bash
uv sync
```

## Usage

### Start the Agent Server
```bash
uv run python main.py
```
The server will start on http://localhost:5001

### Run the Client
In a separate terminal:
```bash
uv run python client.py
```

## How It Works

1. **main.py**: Creates and starts the A2A Starlette application with the RandomNumberAgent
2. **agent_executor.py**: Contains the `RandomNumberAgent` class that:
   - Accepts tasks with descriptions like "Generate a random number between X and Y"
   - Parses the range from the task description
   - Returns a random number within the specified range
3. **client.py**: Sends a sample task to the agent and displays the response

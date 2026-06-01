# 🤖 A2A Simple Agent Example
This repo demonstrates a minimal A2A (Agent-to-Agent) agent implementation using Google's a2a-sdk and python-a2a libraries. The agent is a simple Random Number Generator that responds to A2A-compliant requests by returning a number between 1 and 100.

🧠 This is a great starting point if you're learning A2A and want to see how the low-level agent executor pattern works.

![image](https://github.com/user-attachments/assets/3f915646-d23f-46a7-9fdb-a2f660b20776)


🚀 Quick Start
1. Clone the Repository
```
git clone https://github.com/Marktechpost/AI-Notebooks.git
cd AI-Notebooks/A2A_Simple_Agent
```
2. Set Up Environment
We recommend using uv — a modern Python package manager — for fast setup.

🔧 Install uv
Mac/Linux:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Windows (PowerShell):
```
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

🧪 Create & Activate Virtual Environment
```
uv venv
source .venv/bin/activate  # Use `.venv\Scripts\activate` on Windows
```

📦 Install Dependencies
```
uv sync
```

3. Run the Agent Server
This will start the A2A-compliant agent server on http://localhost:9999.

```
uv run main.py
```
You should see output confirming the server is up and running. The agent card will be served at:
```
http://localhost:9999/.well-known/agent.json
```

4. Run the A2A Client
In a separate terminal (with the same virtual environment activated):
```
uv run client.py
```

✅ This will:

* Fetch the agent card

* Send a sample message: "Give me a random number"

* Print the structured response from the agent

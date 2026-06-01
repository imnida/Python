# ZavaShop Supply-Chain Workshop

A five-lab hands-on workshop teaching **Microsoft Agent Framework** and
**Microsoft Foundry** through ZavaShop, a fictional global e-commerce company
with 5 fulfillment centers and a CEO who wants one live dashboard for all of it.

> **The one mantra: "Read the SKILL first."**
>
> Every LAB README starts by pointing you to a SKILL document. Do not skip it.
> The SKILL is what turns a generic Copilot into a domain-aware engineer.

## The ZavaShop cast

| Agent | Owner | Lab |
|---|---|---|
| **Zara** | Mei Tanaka (Seattle DC supervisor) | LAB01 |
| **Pierre** | Pierre Lefevre (Senior buyer) | LAB02 |
| **Aria** | Lin Zhang (CS director) | LAB03 |
| **Diego's workflow** | Diego Saenz (Fulfillment director) | LAB04 |
| **Control Tower** | CEO | LAB05 |

## Structure

```
workshop/
├── data/                        # Shared fixtures — single source of truth
│   ├── warehouses.json          # 5 fulfillment centers
│   ├── skus.json                # 10 SKUs across 3 categories
│   ├── inventory.json           # 22 stock records
│   ├── purchase_orders.json     # 6 POs (in-transit to delayed)
│   ├── suppliers.json           # 8 suppliers
│   ├── contracts.json           # 5 active supplier contracts
│   ├── customers.json           # 4 customers (3 VIP)
│   ├── orders.json              # 6 orders
│   ├── carriers.json            # 5 shipping carriers
│   ├── exceptions.json          # 4 open supply-chain exceptions
│   └── zava_data.py             # Shared data loader (use this, not raw JSON)
├── LAB01-inventory-agent/       # Single agent: Zara
├── LAB02-procurement-toolbox/   # Toolbox + Agent Skills: Pierre
├── LAB03-customer-memory-eval/  # Memory + Evaluation: Aria
├── LAB04-fulfillment-workflow/  # WorkflowBuilder + HITL: Diego
├── LAB05-control-tower-agui/    # AG-UI dashboard: CEO
└── .env.example                 # Environment template
```

## Setup

### Prerequisites

- Python 3.10+
- Azure subscription with Microsoft Foundry enabled
- `gpt-5.5` and `text-embedding-3-small` deployed in your Foundry project
- `az login` completed

### Install

```bash
pip install agent-framework agent-framework-foundry agent-framework-ag-ui \
    azure-identity python-dotenv fastapi "uvicorn[standard]"
```

### Configure

```bash
cp .env.example .env
# Edit .env: set FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL
```

### Run LAB01

```bash
python LAB01-inventory-agent/zara_agent.py
```

## Lab progression

```
LAB01  →  LAB02  →  LAB03  →  LAB04  →  LAB05
single    toolbox   memory    workflow  dashboard
agent     + skills  + eval    + HITL    (AG-UI)
```

Each lab builds on the previous one. Tools written in LAB01 are reused as
workflow nodes in LAB04. LAB05 shows the live state of every agent.

## Data contract

Every artifact — function tools, workflow executors, AG-UI payloads,
evaluation inputs — loads data through `workshop/data/zava_data.py`.
This keeps numbers consistent across all 5 labs.

```python
from workshop.data.zava_data import find_stock, find_po, load_warehouses

# SKU-7421 @ SEA-01 → on_hand: 312, reorder_point: 100
records = find_stock("SKU-7421", "SEA-01")

# PO-20260518-001 → in_transit, ETA 2026-05-26
po = find_po("PO-20260518-001")
```

**Anti-patterns to avoid:**
- Do not inline mock dicts in tool functions.
- Do not hardcode the model name (use `os.environ["FOUNDRY_MODEL"]`).
- Do not hardcode credentials (use `DefaultAzureCredential()`).
- Do not bypass `zava_data.py` loaders with direct JSON file reads in tools.

## References

- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [Azure AI Foundry documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Blog post: Agents That Build Agents — A SKILL-first Blueprint](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/)

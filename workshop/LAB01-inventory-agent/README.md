# LAB01 — Inventory Agent: Zara

## Story

Mei Tanaka, supervisor at the Seattle Fulfillment Center, gets interrupted 60
times a day by stock-level questions on WeChat, email, and phone:
*"How many SKU-7421 do we have?"*

ZavaShop's first agent, **Zara**, answers those questions in seconds using
real fixture data — no spreadsheets, no manual lookups.

## Read the SKILL first

Before writing or modifying any code, read:

```
.github/skills/agent-framework-azure-ai-py/skill.md
```

The SKILL teaches the framework idioms, import order, naming conventions,
fixture-loading patterns, and anti-patterns. Skip it and you'll write
generic code; read it and you'll write code the team can maintain.

## What Zara does

| Capability | Tool |
|---|---|
| Query stock for any SKU across warehouses | `get_stock()` |
| Check PO status by PO number | `get_po_status()` |
| Find all open POs for a SKU | `find_open_pos()` |
| Look up logistics / shipping docs | `MCPStreamableHTTPTool` → Microsoft Learn |

## Acceptance criteria

- [ ] Turn 1: Stock reply lists all warehouses carrying SKU-7421; SEA-01
      on_hand = **312**, LON-02 flagged as below reorder point (88 < 100).
- [ ] Turn 2: PO answer references **PO-20260518-001** without the user
      repeating the SKU (session context preserved).
- [ ] Turn 3: Reply contains information sourced from Microsoft Learn via MCP.
- [ ] No hardcoded numbers or credentials anywhere in the code.
- [ ] All data loaded via `workshop.data.zava_data` helpers.
- [ ] Resources released cleanly via `async with agent`.

## Setup

```bash
# From the repo root
cd workshop
cp .env.example .env
# Fill in FOUNDRY_PROJECT_ENDPOINT and FOUNDRY_MODEL

pip install agent-framework agent-framework-foundry azure-identity python-dotenv
python LAB01-inventory-agent/zara_agent.py
```

## Key patterns used

```python
# Client targeting Foundry
client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    model=os.environ["FOUNDRY_MODEL"],
    credential=DefaultAzureCredential(),
)

# Agent with function tools + MCP
agent = Agent(client=client, name="Zara", instructions=..., tools=[...])

# Multi-turn session — same session preserves context across turns
session = AgentSession()
async with agent:
    r1 = await agent.run("...", session=session)
    r2 = await agent.run("...", session=session)  # knows context from r1
```

## Data contract

All lookups use shared fixtures from `workshop/data/`. Key values:

| Fixture | Value |
|---|---|
| SKU-7421 @ SEA-01 on_hand | 312 |
| SKU-7421 @ LON-02 on_hand | 88 (below reorder_point 100) |
| Inbound PO for SKU-7421 | PO-20260518-001, in_transit, ETA 2026-05-26 |

## Next

**LAB02** — Pierre's procurement toolbox: Toolbox tools, Agent Skills, and
an approval workflow for high-value POs.

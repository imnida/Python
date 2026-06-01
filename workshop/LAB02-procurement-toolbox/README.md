# LAB02 — Procurement Toolbox: Pierre

## Story

Pierre Lefevre, ZavaShop's senior buyer, manages supplier relationships
across 8 vendors and 5 active contracts. Every high-value PO requires
supervisor approval. Before agents, this was a slow email chain.

**Pierre** is the procurement agent that automates PO validation, contract
lookup, and approval routing using Toolbox tools and Agent Skills.

## Read the SKILL first

```
.github/skills/agent-framework-azure-ai-py/skill.md
```

## What Pierre does

| Capability | Mechanism |
|---|---|
| Look up supplier contracts | Toolbox function tool |
| Validate PO against contract limits | Agent Skill |
| Route high-value POs for approval | Approval workflow + HITL |
| Find open POs by supplier | Toolbox function tool |

## Acceptance criteria

- [ ] Pierre correctly identifies that PO-20260518-001 ($30,800 total) is
      within the Hangzhou Linen Co. contract limit ($200,000).
- [ ] Pierre flags a hypothetical $210,000 PO as exceeding the contract ceiling.
- [ ] Approval routing pauses and waits for human input before continuing.
- [ ] All supplier and contract data loaded from `workshop/data/` fixtures.
- [ ] Tools registered as a Toolbox — not inline function definitions.

## Key patterns (to implement)

```python
from agent_framework.foundry import FoundryChatClient, FoundryToolbox

toolbox = FoundryToolbox(
    name="procurement-tools",
    tools=[validate_po_against_contract, get_supplier_contract, list_open_pos_by_supplier],
)

agent = Agent(
    client=FoundryChatClient(...),
    name="Pierre",
    instructions=PROCUREMENT_INSTRUCTIONS,
    tools=[toolbox],
)
```

## Data contract

| Fixture | Value |
|---|---|
| SUP-002 contract max PO | $200,000 |
| SUP-001 contract max PO | $100,000 |
| PO-20260518-001 total value | 800 × $38.50 = $30,800 |

## Next

**LAB03** — Lin's customer memory system: Foundry Memory, multi-session
preference recall, evaluation, and red-team safety testing.

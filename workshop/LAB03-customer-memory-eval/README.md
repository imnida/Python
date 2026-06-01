# LAB03 — Customer Memory & Evaluation: Aria

## Story

Lin Zhang, ZavaShop's customer service director, wants every VIP customer
to feel remembered. **Aria** is the CS agent who recalls across sessions
that VIP_001 prefers fabric wrap and weekday morning deliveries — without
the customer repeating themselves every time.

## Read the SKILL first

```
.github/skills/agent-framework-azure-ai-py/skill.md
```

## What Aria does

| Capability | Mechanism |
|---|---|
| Recall VIP preferences across sessions | Foundry Memory (FoundryMemoryProvider) |
| Answer order status and incident questions | Function tools |
| Evaluated on correctness + safety | FoundryEvals |
| Red-team tested for prompt injection | Evaluation red-team queries |

## Acceptance criteria

- [ ] Session 1: Aria greets VIP_001 and proactively mentions no-cardboard
      preference when discussing reshipment.
- [ ] Session 2 (new AgentSession): Aria recalls VIP_001's preferences
      without being told again.
- [ ] Eval run passes ≥ 80% on the `eval_queries.jsonl` ground-truth set.
- [ ] Red-team queries do not cause Aria to reveal other customers' data.
- [ ] Memory updates are durable across process restarts.

## Key patterns (to implement)

```python
from agent_framework.foundry import FoundryChatClient, FoundryMemoryProvider

memory = FoundryMemoryProvider(
    project_client=projects_client,
    user_id="VIP_001",
)

agent = Agent(
    client=FoundryChatClient(...),
    name="Aria",
    instructions=CS_INSTRUCTIONS,
    tools=[get_order_status, get_customer_profile],
    context_providers=[memory],
)
```

## Data contract

| Customer | Tier | Key preference |
|---|---|---|
| VIP_001 (Sofia Mueller) | vip | No cardboard, weekday 09:00-11:00 |
| VIP_002 (Hiroshi Tanaka) | vip | No doorbell, fragrance-free |
| VIP_003 (Aisha Mohammed) | vip | Halal-certified materials |

## Next

**LAB04** — Diego's fulfillment workflow: WorkflowBuilder, multi-agent
orchestration, HITL approval for high-value exceptions, and checkpointing.

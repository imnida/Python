# LAB04 — Fulfillment Workflow: Diego

## Story

Diego Saenz, ZavaShop's fulfillment director, handles a $10K+ supply chain
exception every day. Before agents: a 5-team email chain. After agents: a
WorkflowBuilder graph with one HITL approval step and a full audit trail.

## Read the SKILL first

```
.github/skills/agent-framework-workflows-py/skill.md
```

## What Diego's workflow does

| Step | Agent/Action |
|---|---|
| Triage exception | Zara (inventory agent) checks nearest stock |
| Evaluate severity | Rule node: severity ≥ high → HITL |
| Human approval | HITL pause — Diego approves or rejects |
| Execute reroute | Fulfillment action: reroute from alternate DC |
| Notify CS | Aria (CS agent) drafts customer comms |
| Checkpoint | Workflow state saved; survives process restart |

## Acceptance criteria

- [ ] Workflow correctly routes ORD-20260525-009 (SKU-6190, LON-02 out-of-stock)
      to SEA-01 as the alternate source.
- [ ] HITL pause fires for orders ≥ `high` severity; auto-approves `low`.
- [ ] Workflow resumes from checkpoint after simulated process restart.
- [ ] All agents in the workflow reuse tools from LAB01/LAB02 — no code
      duplication.
- [ ] End-to-end trace visible in Azure Monitor / App Insights.

## Key patterns (to implement)

```python
from agent_framework import WorkflowBuilder, HumanInTheLoopStep

workflow = (
    WorkflowBuilder()
    .add_agent(zara, name="triage")
    .add_condition(route_by_severity, name="severity_gate")
    .add_hitl(approver="diego@zavashop.example.com", name="approval")
    .add_agent(fulfillment_executor, name="reroute")
    .add_agent(aria, name="notify_cs")
    .with_checkpoint(storage=checkpoint_store)
    .build()
)

result = await workflow.run(exception_payload)
```

## Data contract

| Exception | Order | Severity | Resolution |
|---|---|---|---|
| OUT_OF_STOCK | ORD-20260525-009 | high | Reroute from SEA-01 |
| AMOUNT_OVER_THRESHOLD | ORD-20260524-002 | low | Auto-approve |

## Next

**LAB05** — CEO's AG-UI control tower: a React + AG-UI dashboard showing
live workflow state, inventory alerts, and exception queue for all 5 DCs.

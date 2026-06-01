# LAB05 — AG-UI Control Tower

## Story

ZavaShop's CEO wants one live dashboard covering all 5 fulfillment centers:
inventory alerts, open exceptions, PO pipeline, and workflow approvals —
all in one place.

**LAB05** builds the AG-UI server (FastAPI + SSE) and the React frontend
that plugs into it. Every agent in the stack feeds the same control tower.

## Read the SKILL first

```
.github/skills/agent-framework-agui-py/skill.md
```

## What the control tower shows

| Panel | Data source |
|---|---|
| Inventory alerts | Zara (LAB01) — SKUs below reorder point |
| Open exceptions queue | `exceptions.json` fixtures |
| PO pipeline | Pierre (LAB02) — in-transit and delayed POs |
| Workflow live status | Diego (LAB04) — WorkflowBuilder event stream |
| HITL approval inbox | Pending approvals requiring human action |

## Acceptance criteria

- [ ] AG-UI server starts on `http://127.0.0.1:5100/` with auth header check.
- [ ] SSE stream delivers inventory alerts within 2 seconds of startup.
- [ ] React frontend renders exception queue with severity badges.
- [ ] HITL approval button triggers LAB04 workflow resumption.
- [ ] All 7 AG-UI features exercised: SSE, generative UI, HITL, shared state,
      frontend tools, backend tools, and streaming text.

## Key patterns (to implement)

```python
from agent_framework.ag_ui import AGUIServer, AGUIRouter

router = AGUIRouter()

@router.on_run
async def handle_run(input: AGUIRunInput) -> AsyncIterator[AGUIEvent]:
    async for event in zara.stream(input.messages, session=input.session):
        yield event

app = AGUIServer(router=router, api_key=os.environ["AG_UI_API_KEY"])
```

## Setup

```bash
pip install agent-framework agent-framework-foundry agent-framework-ag-ui \
    fastapi "uvicorn[standard]" azure-identity python-dotenv

# Start the AG-UI server
uvicorn LAB05-control-tower-agui.server:app --port 5100 --reload

# In another terminal, start the React frontend
cd LAB05-control-tower-agui/frontend
npm install && npm run dev
```

"""
LAB01 — Zara, ZavaShop Inventory Agent

Zara answers warehouse stock and purchase-order questions for Mei Tanaka,
the Seattle Fulfillment Center supervisor who gets hit 60 times a day with
"how many SKU-7421 do we have?"

Run:
    cd workshop
    python LAB01-inventory-agent/zara_agent.py

Prerequisites:
    pip install agent-framework agent-framework-foundry azure-identity python-dotenv
    Copy .env.example → .env and set FOUNDRY_PROJECT_ENDPOINT + FOUNDRY_MODEL
"""

import asyncio
import os
import pathlib
import sys

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# Allow imports from the workshop root so zava_data is reachable.
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))

from agent_framework import Agent, AgentSession, MCPStreamableHTTPTool
from agent_framework.foundry import FoundryChatClient

from workshop.data.zava_data import find_open_pos_by_sku, find_po, find_stock

# Load environment from workshop/.env (falls back to repo-root .env)
load_dotenv(pathlib.Path(__file__).parent.parent / ".env")
load_dotenv()

_INSTRUCTIONS = """\
You are Zara, ZavaShop's warehouse assistant. You help warehouse supervisors
and operations staff get fast, accurate answers about stock levels, inbound
purchase orders, and logistics documentation.

Guidelines:
- Always look up data using your tools — never invent numbers.
- When asked about stock without a warehouse, report all warehouses that carry
  the SKU, then flag any location below the reorder point.
- Quote exact field values from the fixtures (on_hand, reserved, eta, etc.).
- Keep replies concise; bullet points work well for multi-location answers.
- If a SKU or PO is not found, say so explicitly rather than guessing.
"""


def get_stock(sku: str, warehouse: str = "") -> dict:
    """
    Return current stock levels for a SKU.

    Args:
        sku: The SKU identifier (e.g. SKU-7421).
        warehouse: Optional warehouse code to filter (e.g. SEA-01). Leave
                   blank to get all locations.

    Returns:
        Dict with 'records' list and 'below_reorder' list of warehouse codes
        where on_hand is below reorder_point.
    """
    records = find_stock(sku, warehouse if warehouse else None)
    if not records:
        return {"records": [], "below_reorder": [], "message": f"No inventory found for {sku}"}

    below_reorder = [
        r["warehouse"]
        for r in records
        if r["on_hand"] < r["reorder_point"]
    ]
    return {"records": records, "below_reorder": below_reorder}


def get_po_status(po_number: str) -> dict:
    """
    Return status and details for a purchase order.

    Args:
        po_number: The PO number (e.g. PO-20260518-001).

    Returns:
        The purchase order record, or a not-found message.
    """
    po = find_po(po_number)
    if po is None:
        return {"found": False, "message": f"Purchase order {po_number} not found."}
    return {"found": True, **po}


def find_open_pos(sku: str) -> dict:
    """
    Return all open (non-delivered) purchase orders for a SKU.

    Args:
        sku: The SKU identifier (e.g. SKU-7421).

    Returns:
        Dict with 'pos' list of matching purchase orders.
    """
    pos = find_open_pos_by_sku(sku)
    return {"pos": pos, "count": len(pos)}


async def main() -> None:
    credential = DefaultAzureCredential()

    mcp_tool = MCPStreamableHTTPTool(
        name="ms_learn_logistics",
        description=(
            "Microsoft Learn logistics handbook. Use this to look up shipping "
            "regulations, hazmat rules, incoterm definitions, and carrier SLAs."
        ),
        url="https://learn.microsoft.com/api/mcp",
    )

    agent = Agent(
        client=FoundryChatClient(
            project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
            model=os.environ["FOUNDRY_MODEL"],
            credential=credential,
        ),
        name="Zara",
        instructions=_INSTRUCTIONS,
        tools=[get_stock, get_po_status, find_open_pos, mcp_tool],
    )

    session = AgentSession()

    print("=" * 60)
    print("ZavaShop — Zara Inventory Agent (LAB01)")
    print("=" * 60)

    async with agent:
        # Turn 1 — stock query
        turn1 = "How many SKU-7421 do we have across all warehouses? Flag any location below the reorder point."
        print(f"\nUser: {turn1}")
        r1 = await agent.run(turn1, session=session)
        print(f"Zara: {r1}")

        # Turn 2 — follow-up without repeating the SKU (tests session context)
        turn2 = "What's the status of the inbound PO for that SKU?"
        print(f"\nUser: {turn2}")
        r2 = await agent.run(turn2, session=session)
        print(f"Zara: {r2}")

        # Turn 3 — MCP question to verify the handbook tool is wired up
        turn3 = "What does Microsoft Learn say about FOB Ningbo shipping terms?"
        print(f"\nUser: {turn3}")
        r3 = await agent.run(turn3, session=session)
        print(f"Zara: {r3}")

    print("\n" + "=" * 60)
    print("Session complete.")


if __name__ == "__main__":
    asyncio.run(main())

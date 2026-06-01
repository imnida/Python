"""
ZavaShop shared fixture loader.

Plain Python lists / dicts — no SDK types — so the data is reusable from
function tools, evaluation inputs, AG-UI server payloads, and workflow
executors alike.

Usage:
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent.parent.parent))
    from workshop.data.zava_data import find_stock, find_po, load_warehouses
"""

import json
import pathlib
from functools import lru_cache
from typing import Any

_DATA_DIR = pathlib.Path(__file__).parent


def _read_json(filename: str) -> list[dict[str, Any]]:
    with open(_DATA_DIR / filename, encoding="utf-8") as f:
        return json.load(f)


def _read_jsonl(filename: str) -> list[dict[str, Any]]:
    path = _DATA_DIR / filename
    if not path.exists():
        return []
    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


@lru_cache(maxsize=1)
def load_warehouses() -> list[dict[str, Any]]:
    return _read_json("warehouses.json")


@lru_cache(maxsize=1)
def load_skus() -> list[dict[str, Any]]:
    return _read_json("skus.json")


@lru_cache(maxsize=1)
def load_inventory() -> list[dict[str, Any]]:
    return _read_json("inventory.json")


@lru_cache(maxsize=1)
def load_purchase_orders() -> list[dict[str, Any]]:
    return _read_json("purchase_orders.json")


@lru_cache(maxsize=1)
def load_suppliers() -> list[dict[str, Any]]:
    return _read_json("suppliers.json")


@lru_cache(maxsize=1)
def load_contracts() -> list[dict[str, Any]]:
    return _read_json("contracts.json")


@lru_cache(maxsize=1)
def load_customers() -> list[dict[str, Any]]:
    return _read_json("customers.json")


@lru_cache(maxsize=1)
def load_orders() -> list[dict[str, Any]]:
    return _read_json("orders.json")


@lru_cache(maxsize=1)
def load_carriers() -> list[dict[str, Any]]:
    return _read_json("carriers.json")


@lru_cache(maxsize=1)
def load_exceptions() -> list[dict[str, Any]]:
    return _read_json("exceptions.json")


@lru_cache(maxsize=1)
def load_eval_queries() -> list[dict[str, Any]]:
    return _read_jsonl("eval_queries.jsonl")


# ---------------------------------------------------------------------------
# Helper lookups
# ---------------------------------------------------------------------------

def find_stock(sku: str, warehouse: str | None = None) -> list[dict[str, Any]]:
    """Return inventory records for a SKU, optionally filtered by warehouse."""
    rows = load_inventory()
    results = [r for r in rows if r["sku"].upper() == sku.upper()]
    if warehouse:
        results = [r for r in results if r["warehouse"].upper() == warehouse.upper()]
    return results


def find_po(po_number: str) -> dict[str, Any] | None:
    """Return the purchase order matching po_number, or None."""
    pos = load_purchase_orders()
    for po in pos:
        if po["po_number"].upper() == po_number.upper():
            return po
    return None


def find_open_pos_by_sku(sku: str) -> list[dict[str, Any]]:
    """Return all non-delivered purchase orders for a given SKU."""
    pos = load_purchase_orders()
    return [
        po for po in pos
        if po["sku"].upper() == sku.upper() and po["status"] != "delivered"
    ]


def find_supplier(supplier_id: str | None = None, name: str | None = None) -> dict[str, Any] | None:
    """Look up a supplier by ID or partial case-insensitive name."""
    suppliers = load_suppliers()
    if supplier_id:
        for s in suppliers:
            if s["supplier_id"].upper() == supplier_id.upper():
                return s
    if name:
        name_lower = name.lower()
        for s in suppliers:
            if name_lower in s["name"].lower():
                return s
    return None


def find_contract(supplier_id: str) -> dict[str, Any] | None:
    """Return the active contract for a supplier."""
    contracts = load_contracts()
    for c in contracts:
        if c["supplier_id"].upper() == supplier_id.upper():
            return c
    return None


def find_customer(customer_id: str) -> dict[str, Any] | None:
    """Return a customer record by ID."""
    customers = load_customers()
    for c in customers:
        if c["customer_id"].upper() == customer_id.upper():
            return c
    return None


def find_order(order_id: str) -> dict[str, Any] | None:
    """Return an order record by ID."""
    orders = load_orders()
    for o in orders:
        if o["order_id"].upper() == order_id.upper():
            return o
    return None

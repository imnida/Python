#!/usr/bin/env python3
"""
Agentic OS Memory Manager

Commands:
  save <topic> <summary>   Save a new memory
  list                     List all saved memories
  search <query>           Search memories by keyword
  show <id>                Show full text of a memory
  delete <id>              Delete a memory
  sync                     Rebuild memory.md from the store (run after edits)
"""

import sys
import json
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent
STORE_DIR = BASE_DIR / "memory_store"
MEMORY_MD = BASE_DIR / "memory.md"
INDEX_FILE = STORE_DIR / "index.json"
MEMORY_CAP = 2500


def _ensure_store():
    STORE_DIR.mkdir(exist_ok=True)
    if not INDEX_FILE.exists():
        INDEX_FILE.write_text(json.dumps([], indent=2))


def _load_index() -> list:
    _ensure_store()
    return json.loads(INDEX_FILE.read_text())


def _save_index(index: list):
    INDEX_FILE.write_text(json.dumps(index, indent=2))


def cmd_save(topic: str, summary: str):
    index = _load_index()
    ts = datetime.now()
    base_id = ts.strftime("%Y%m%d_%H%M%S")
    existing_ids = {e["id"] for e in index}
    memory_id = base_id
    counter = 1
    while memory_id in existing_ids:
        memory_id = f"{base_id}_{counter}"
        counter += 1

    entry = {
        "id": memory_id,
        "topic": topic,
        "summary": summary,
        "created": ts.isoformat(),
    }

    mem_file = STORE_DIR / f"{memory_id}.md"
    mem_file.write_text(
        f"# {topic}\n\n{summary}\n\n_Saved: {ts.strftime('%Y-%m-%d %H:%M')}_\n"
    )

    index.append(entry)
    _save_index(index)
    print(f"Saved [{memory_id}]: {topic}")
    cmd_sync(quiet=True)


def cmd_list():
    index = _load_index()
    if not index:
        print("No memories saved yet.")
        return
    for entry in sorted(index, key=lambda x: x["created"], reverse=True):
        short = entry["summary"][:80] + ("..." if len(entry["summary"]) > 80 else "")
        print(f"[{entry['id']}] {entry['topic']}")
        print(f"    {short}")
        print(f"    {entry['created'][:10]}")


def cmd_search(query: str):
    index = _load_index()
    q = query.lower()
    results = [
        e for e in index
        if q in e["topic"].lower() or q in e["summary"].lower()
    ]
    if not results:
        print(f"No memories matched: {query!r}")
        return
    print(f"{len(results)} result(s):\n")
    for entry in results:
        print(f"[{entry['id']}] {entry['topic']}")
        print(f"    {entry['summary']}")
        print(f"    {entry['created'][:10]}\n")


def cmd_show(memory_id: str):
    mem_file = STORE_DIR / f"{memory_id}.md"
    if not mem_file.exists():
        print(f"Not found: {memory_id}")
        sys.exit(1)
    print(mem_file.read_text())


def cmd_delete(memory_id: str):
    index = _load_index()
    new_index = [e for e in index if e["id"] != memory_id]
    if len(new_index) == len(index):
        print(f"Not found: {memory_id}")
        sys.exit(1)
    _save_index(new_index)
    mem_file = STORE_DIR / f"{memory_id}.md"
    if mem_file.exists():
        mem_file.unlink()
    print(f"Deleted: {memory_id}")
    cmd_sync(quiet=True)


def cmd_sync(quiet: bool = False):
    """Rebuild memory.md from recent entries, capped at MEMORY_CAP chars."""
    index = _load_index()
    entries = sorted(index, key=lambda x: x["created"], reverse=True)

    header = (
        f"# Recent Memory\n\n"
        f"_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n\n"
    )
    body_parts = []
    char_count = len(header)

    for entry in entries:
        block = f"## {entry['topic']}\n{entry['summary']}\n_{entry['created'][:10]}_\n\n"
        if char_count + len(block) > MEMORY_CAP:
            break
        body_parts.append(block)
        char_count += len(block)

    if not body_parts:
        if entries:
            footer = "_Memory store has entries but none fit the cap. Run `list` to review._\n"
        else:
            footer = "_No memories saved yet._\n"
        body_parts.append(footer)

    MEMORY_MD.write_text(header + "".join(body_parts))
    if not quiet:
        print(f"Synced memory.md — {len(body_parts)} entries, {char_count} chars")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    cmd = sys.argv[1]
    args = sys.argv[2:]

    dispatch = {
        "save":   lambda: cmd_save(args[0], args[1]) if len(args) >= 2 else _usage("save <topic> <summary>"),
        "list":   lambda: cmd_list(),
        "search": lambda: cmd_search(args[0]) if args else _usage("search <query>"),
        "show":   lambda: cmd_show(args[0]) if args else _usage("show <id>"),
        "delete": lambda: cmd_delete(args[0]) if args else _usage("delete <id>"),
        "sync":   lambda: cmd_sync(),
    }

    if cmd not in dispatch:
        print(f"Unknown command: {cmd}\n")
        print(__doc__)
        sys.exit(1)

    dispatch[cmd]()


def _usage(hint: str):
    print(f"Usage: memory_manager.py {hint}")
    sys.exit(1)


if __name__ == "__main__":
    main()

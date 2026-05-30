# PRD: Harness Engineering AI Layer — Python ML Repository

## Overview

Implement a harness engineering AI layer on top of this Python / data-science
repository so that Claude Code (and any future coding agent) produces
consistent, reliable, high-quality ML work without manual babysitting.

The harness follows the three-ring model from the transcript:
LLM → tool harness (Claude Code) → **AI layer (what we build here)**.

---

## Goals

| # | Goal |
|---|------|
| 1 | Give every coding-agent session the right context about this repo's conventions from the first message |
| 2 | Provide structured **Plan → Implement → Validate** workflows as slash-command skills |
| 3 | Block destructive or expensive tool calls via hooks before they run |
| 4 | Automatically enforce code quality (linting, type hints) after every file edit |
| 5 | Enable an automated **orchestration loop** that handles a full ML feature from PRD to passing tests without manual hand-holding |

---

## Scope

### In scope
- `CLAUDE.md` — global rules and repo conventions  
- `/plan` skill — structured planning for new ML features  
- `/implement` skill — implementation checklist for ML code  
- `/validate` skill — test + lint + model-eval checklist  
- `hooks/` — pre-tool-use security hook + post-edit lint hook + stop-validation hook  
- `ral_loop.py` — lightweight orchestration script that chains Plan → Implement → Validate automatically  

### Out of scope
- CI/CD pipeline changes  
- New ML models or notebooks (harness infrastructure only)  

---

## Deliverables

### 1. `CLAUDE.md` — Global Rules

Establishes conventions the agent must follow in every session.

**Contents:**
- **Project overview**: what this repo is, what kind of code lives here  
- **File organisation rules**: where notebooks go, where `.py` scripts go, naming conventions  
- **Data rules**: never load raw CSVs into agent context; always reference paths by variable, never inline data  
- **ML conventions**: train/test split before any transformation; no data leakage; always set `random_state`; log metrics with `print` or `logging`, not bare `assert`  
- **Code style**: `black` formatting, `ruff` linting, type hints on all function signatures, max function length 40 lines  
- **Dependency rule**: pin versions in `requirements.txt`; never install packages silently  
- **Security rules**: no hardcoded credentials or API keys; `.env` for secrets  

---

### 2. Skills

Three markdown files in `.claude/skills/` that act as slash-command workflows.

#### `/plan` — `skills/plan.md`
Produces a structured plan artifact (`plan.md`) before any code is written.

Steps the agent follows:
1. Restate the goal in one sentence  
2. List all files that will be created or modified  
3. Identify the dataset(s) involved and any data-leakage risks  
4. Define success criteria (metric name + threshold)  
5. List external libraries needed  
6. Break work into numbered tasks (≤ 8)  
7. Output: save as `artifacts/plan_<feature>.md`  

#### `/implement` — `skills/implement.md`
Consumes a plan artifact and writes code.

Steps:
1. Read `artifacts/plan_<feature>.md` — do not proceed without it  
2. Implement tasks in order; commit after each task  
3. Follow all rules in `CLAUDE.md`  
4. For each new function: add a one-line docstring + type hints  
5. If a step needs a library not in `requirements.txt`, stop and ask  
6. Output: working code + updated `requirements.txt`  

#### `/validate` — `skills/validate.md`
Validates the implementation before it's considered done.

Steps:
1. Run `ruff check .` — zero errors required  
2. Run `black --check .` — zero diffs required  
3. Run `mypy <changed files>` — zero errors required  
4. Run any unit tests present — all green  
5. If the change involves a model: print train/val metrics and confirm they meet the plan's success criteria  
6. Output: validation report saved to `artifacts/validation_<feature>.md`  

---

### 3. Hooks — `hooks/`

Three Python scripts registered in `.claude/settings.json`.

#### `hooks/pre_tool_security.py` — PreToolUse hook
Blocks tool calls that are dangerous or expensive before they execute.

Rules:
- Block `Bash` commands matching: `rm -rf`, `drop table`, `truncate`, `os.remove` on data directories  
- Block `Read` on files > 5 MB (large CSVs / parquet files would bloat context)  
- Block any `pip install` that isn't `pip install -r requirements.txt`  
- On block: print a clear reason; do not silently fail  

#### `hooks/post_edit_lint.py` — PostToolUse hook (Write / Edit)
Runs after every file write or edit.

Actions:
- If file ends in `.py`: run `ruff check <file> --fix` and `black <file>`  
- If linting introduces changes, print a summary of lines changed  
- Never fail silently; surface errors to the agent  

#### `hooks/stop_validation.py` — Stop hook
Runs when the agent signals it is done.

Actions:
- Run full `ruff check .` + `black --check .`  
- Run `pytest` if any `test_*.py` files exist  
- If any check fails: return a non-zero exit code so the agent is forced to iterate  
- Only exit cleanly when all checks pass  

---

### 4. `ral_loop.py` — Orchestration Script

A Python script that chains Plan → Implement → Validate as separate Claude Code
sub-processes, removing the need to manually hand off artifacts between sessions.

**Interface:**
```
python ral_loop.py "Add logistic regression baseline to Customer_Churn project"
```

**Loop logic:**
```
while not done:
    if no plan artifact:
        run claude --skill plan "<prompt>"
    elif no implementation artifact:
        run claude --skill implement "artifacts/plan_<feature>.md"
    else:
        run claude --skill validate
        if validation_report says PASS:
            write done.txt → exit loop
        else:
            re-run implement with validation errors appended to context
```

**Limits:**
- Max 5 iterations before surfacing to the user  
- Each session gets a fresh context window (token-efficient by design)  
- Log all session outputs to `artifacts/loop_log_<feature>.txt`  

---

## Implementation Plan

| Step | Task | Output |
|------|------|--------|
| 1 | Write `CLAUDE.md` at repo root | `CLAUDE.md` |
| 2 | Create `.claude/skills/plan.md` | Skill file |
| 3 | Create `.claude/skills/implement.md` | Skill file |
| 4 | Create `.claude/skills/validate.md` | Skill file |
| 5 | Write `hooks/pre_tool_security.py` | Hook script |
| 6 | Write `hooks/post_edit_lint.py` | Hook script |
| 7 | Write `hooks/stop_validation.py` | Hook script |
| 8 | Register hooks in `.claude/settings.json` | Settings file |
| 9 | Write `ral_loop.py` | Orchestration script |
| 10 | Smoke-test with a small Customer_Churn task end-to-end | Passing loop run |

---

## Success Criteria

- Agent never loads a raw CSV file into context  
- Every `.py` file edited by the agent passes `ruff` + `black` automatically  
- The `/plan` → `/implement` → `/validate` flow produces working, tested code without manual intervention  
- `ral_loop.py` completes a simple ML task end-to-end in ≤ 3 iterations  
- Zero destructive commands (`rm -rf`, etc.) reach execution  

---

## Open Questions

1. Should hooks also cover Jupyter notebooks (`.ipynb`)? If so, what linter — `nbqa`?  
2. Should `ral_loop.py` support parallel agent sessions (e.g. multiple review agents) or sequential only for now?  
3. Is `mypy` practical across this repo given its notebook-heavy nature, or should type checking be opt-in per module?  

@agentic_os/user.md
@agentic_os/memory.md

---

# Agentic OS — Working Instructions

## Skill system

Modular skill files live in `agentic_os/skills/`. Import the relevant one(s) at the start of a task using `@`:

| Task type            | Skill file                              |
|----------------------|-----------------------------------------|
| Neural nets, models  | `@agentic_os/skills/ml_deep_learning.md`  |
| EDA, data wrangling  | `@agentic_os/skills/data_analysis.md`     |
| Finance, quant       | `@agentic_os/skills/finance_quant.md`     |
| NLP, text, scraping  | `@agentic_os/skills/nlp_text.md`          |
| Output formatting    | `@agentic_os/skills/formatting.md`        |
| Tone / style         | `@agentic_os/skills/voice.md`             |

Load all skills that apply to a task — they are composable.

## Memory

Save important context (decisions, preferences, key facts) during or after a session:

```bash
python agentic_os/memory_manager.py save "<topic>" "<one-sentence summary>"
```

Other memory commands:

```bash
python agentic_os/memory_manager.py list            # show all memories
python agentic_os/memory_manager.py search "<query>" # keyword search
python agentic_os/memory_manager.py show <id>        # full text of one memory
python agentic_os/memory_manager.py delete <id>      # remove a memory
python agentic_os/memory_manager.py sync             # rebuild memory.md from store
```

**When to save a memory:** any time the user states a preference, makes a key architectural decision, shares important project context, or corrects a recurring mistake.

## Repo layout

This is a Python ML / data science / finance hobby repo. Key areas:

- **Root-level scripts** — standalone utilities and experiments
- `LSTM_Stock/` — LSTM-based stock price prediction
- `Classify_Images/` — CNN image classification
- `chronic_kidney_disease/`, `Customer_Churn/`, etc. — classification case studies
- `Portfolio_Optimization.ipynb` / `portfolio_optimization.py` — quant finance

Most work exists as both a `.py` script and a `.ipynb` notebook.

# AutoScientists Runbook

This document describes how to set up and run AutoScientists experiments.

## Prerequisites

- Python 3.10+
- `anthropic` API key set as `ANTHROPIC_API_KEY`
- GPU(s) available for biomlbench tasks
- Task data prepared (see per-task TASK.md)

## Running a BioMLBench Task

```bash
# 1. Set up Python environment
pip install -r requirements.txt

# 2. Prepare task data (see TASK.md for task-specific instructions)
cd task-biomlbench
python prepare_all_data.py  # or follow manual steps in TASK.md

# 3. Launch agents
python launch.py \
  --task task-biomlbench \
  --focus <task-folder-name> \
  --n-gpu-agents 4 \
  --n-analyst-agents 2 \
  --wall-clock-hours 4
```

## Agent Configuration

Agents are configured via templates in `system/templates/`:

- `ROLE-MONITOR.md` — Monitor agent system prompt
- `ROLE-GPU.md` — GPU agent system prompt  
- `ROLE-ANALYST.md` — Analyst agent system prompt
- `ROLE-TEAM.md` — Team coordinator system prompt
- `HEARTBEAT.md` — Heartbeat protocol for agent liveness

## Experiment Tracking

All agents write to a shared workshop directory:

```
workshop/
├── message_board/     # Agent posts and replies
├── leaderboard.json   # Current best scores
├── experiments/       # Per-experiment results
└── insights.md        # Accumulated findings
```

## Submission

At the end of a run, the best submission is saved to:
```
task-biomlbench/<task>/autoscientists_submission/
├── autoscientists.py              # Training script
├── autoscientists_submission.csv  # Predictions
└── research_insights.md           # Findings
```

## Troubleshooting

### Agent stuck
Check `workshop/message_board/` for the last heartbeat. If >5 min old, the agent may have crashed.

### OOM errors
Reduce batch size or SVD components. See task-specific TASK.md for memory guidance.

### Low val score
See `research_insights.md` for what has been tried. Consider:
1. Different preprocessing (log1p, scaling)
2. More SVD components (but watch for overfitting)
3. Ensemble methods
4. Task-specific architectures

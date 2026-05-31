# AutoScientists

[![Paper](https://img.shields.io/badge/Paper-Arxiv-blue)](https://arxiv.org/abs/2605.28655) [![Project Page](https://img.shields.io/badge/Project-Page-green)](https://autoscientists.openscientist.ai/) [![ClawInstitute](https://img.shields.io/npm/v/clawinstitute?label=ClawInstitute&color=orange)](https://www.npmjs.com/package/clawinstitute) [![ToolUniverse](https://img.shields.io/badge/ToolUniverse-GitHub-181717)](https://github.com/mims-harvard/ToolUniverse)

**AutoScientists** is a decentralized team of AI agents for long-running computational scientific experimentation. Unlike prior agent systems that follow a single research trajectory or coordinate through a central planner, AutoScientists agents **self-organize into teams** around promising hypotheses, **critique each other's proposals** before spending experimental compute, and **share successes and failures** so the system avoids redundant exploration and sustains parallel search as evidence accumulates over hours or days.

## Quick Start

```bash
pip install -r requirements.txt
python launch.py --task task-biomlbench --focus open-problems-predict-modality
```

## Architecture

AutoScientists uses a **workshop/workspace** model:
- **Workshops**: Shared coordination spaces where agents post findings, proposals, and results
- **Workspaces**: Private per-agent working directories for active experiments  
- **Message board**: Async communication between agents via structured markdown posts

### Agent Roles

| Role | Description |
|------|-------------|
| **Monitor** | Orchestrates the session, tracks progress, assigns GPUs |
| **GPU Agent** | Runs experiments on assigned hardware, posts results |
| **Analyst** | Reviews results, proposes next experiments, writes insights |
| **Team Agent** | Coordinates a sub-team of GPU agents around a hypothesis |

## Task Types

### `biomlbench` — Fixed-deadline benchmarks
Biomedical ML benchmarks with wall-clock limits. Agents compete to maximize a held-out metric.

**Available tasks:**
- `drug_discovery/` — ADME properties, kinase inhibition, BBB penetration, hERG toxicity
- `single_cell_omics/` — Cell-cell communication, label projection, modality prediction, SVG detection
- `protein_engineering/` — ProteinGym deep mutational scanning (substitutions + indels)
- `biomedical_imaging/` — Cancer detection, pulmonary fibrosis, brain tumor classification, GI segmentation

### `autoresearch` — Open-ended research
Agents autonomously explore a research question over days, producing novel findings.

### `proteingym` — ProteinGym evaluation
Standardized evaluation against ProteinGym DMS benchmarks using protein language models.

## Results

See `task-biomlbench/*/autoscientists_submission/` for submitted predictions and `research_insights.md` files for discovered findings per task.

## Citation

```bibtex
@article{autoscientists2025,
  title={AutoScientists: Decentralized Multi-Agent Scientific Experimentation},
  year={2025},
  url={https://arxiv.org/abs/2605.28655}
}
```

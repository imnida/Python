# Formatting Skill

## Code
- Always use fenced code blocks with language tags (```python, ```bash, etc.)
- Keep line length under 100 chars
- Use descriptive variable names — avoid single-letter names outside of math/loop indices

## Written responses
- Use headers (##) to separate major sections in long responses
- Prefer bullet lists over dense paragraphs for enumerable items
- Include a short summary at the top for responses longer than ~300 words

## ML outputs
- Always include: model architecture summary, training config (epochs, batch size, optimizer)
- Show sample predictions alongside ground truth when evaluating
- Plot training history (loss + accuracy/metric per epoch) when training a model

## Finance outputs
- Always state the date range of analysis
- Round percentages to 2 decimal places
- Label axes fully on all charts (units, time period)
- Note data source and any survivorship bias or look-ahead bias assumptions

## Notebooks vs scripts
- Notebooks: narrative cells explaining each section, visualizations inline
- Scripts: minimal prose, let code speak; add a CLI `argparse` section if the script takes inputs

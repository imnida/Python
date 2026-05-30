import json
import re
from typing import Any

from .config import Config, LLMConfig
from .models import FileDiff, ReviewComment

SYSTEM_PROMPT = """\
You are an expert code reviewer. Analyze the provided git diff and give precise, \
actionable feedback. Focus on:
- Bugs and logic errors
- Security vulnerabilities (SQL injection, XSS, command injection, etc.)
- Performance issues
- Null/None pointer risks
- Thread safety and concurrency bugs
- Code style and maintainability issues

Respond ONLY with a JSON object in this exact format:
{
  "summary": "One-sentence overall assessment.",
  "comments": [
    {
      "file": "path/to/file.py",
      "line": 42,
      "severity": "error|warning|info|suggestion",
      "message": "Clear description of the issue.",
      "suggestion": "Optional: what to do instead."
    }
  ]
}

- "line" should be the line number in the new file where the issue occurs (null if not applicable).
- Be concise. Only report real issues — not style nits unless they matter.
- Do not include any text outside the JSON object.
"""


def _build_diff_prompt(files: list[FileDiff]) -> str:
    parts = []
    for f in files:
        lang = f.language or "text"
        header = f"### File: {f.path}"
        if f.is_new:
            header += " (new file)"
        elif f.is_deleted:
            header += " (deleted)"
        elif f.old_path:
            header += f" (renamed from {f.old_path})"
        parts.append(header)
        parts.append(f"```{lang}")
        parts.append(f.full_diff())
        parts.append("```")
    return "\n".join(parts)


def _parse_response(text: str) -> tuple[str, list[ReviewComment]]:
    """Extract JSON from LLM response and parse into ReviewComments."""
    # Strip markdown code fences if present
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    try:
        data: dict[str, Any] = json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON object from text
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            data = json.loads(m.group())
        else:
            return "Could not parse LLM response.", []

    summary = data.get("summary", "")
    comments = []
    for raw in data.get("comments", []):
        comments.append(ReviewComment(
            file=raw.get("file", ""),
            line=raw.get("line"),
            severity=raw.get("severity", "info"),
            message=raw.get("message", ""),
            suggestion=raw.get("suggestion"),
        ))
    return summary, comments


def _call_anthropic(cfg: LLMConfig, prompt: str) -> str:
    import anthropic  # type: ignore

    kwargs: dict[str, Any] = {"api_key": cfg.api_key}
    if cfg.base_url:
        kwargs["base_url"] = cfg.base_url

    client = anthropic.Anthropic(**kwargs)
    message = client.messages.create(
        model=cfg.model,
        max_tokens=cfg.max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _call_openai(cfg: LLMConfig, prompt: str) -> str:
    import openai  # type: ignore

    kwargs: dict[str, Any] = {"api_key": cfg.api_key}
    if cfg.base_url:
        kwargs["base_url"] = cfg.base_url

    client = openai.OpenAI(**kwargs)
    response = client.chat.completions.create(
        model=cfg.model,
        max_tokens=cfg.max_tokens,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content or ""


def review_bundle(files: list[FileDiff], config: Config) -> tuple[str, list[ReviewComment]]:
    """Send a bundle of file diffs to the LLM and return (summary, comments)."""
    prompt = _build_diff_prompt(files)

    if config.llm.provider == "anthropic":
        raw = _call_anthropic(config.llm, prompt)
    else:
        raw = _call_openai(config.llm, prompt)

    return _parse_response(raw)

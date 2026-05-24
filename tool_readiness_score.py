"""
Tool readiness scorer for LLM-native harnesses.

Evaluates whether a Python function's documentation and type annotations
are sufficient for a LLM to use it correctly. Functions scoring below
the threshold should not be exposed to an agent until improved.

Usage:
    score, report = evaluate_tool(save_architecture_element)
    if score < READINESS_THRESHOLD:
        raise ValueError(f"Tool not LLM-ready:\n{report}")
"""

import inspect
import re
from dataclasses import dataclass, field
from typing import Any, Callable, get_type_hints


READINESS_THRESHOLD = 0.7

# Domain vocabulary signals — extend per project
DOMAIN_VOCABULARY = [
    "togaf", "archimate", "ea360", "business process",
    "application component", "data object", "stakeholder",
]


@dataclass
class ReadinessReport:
    tool_name: str
    score: float
    checks: dict[str, tuple[bool, str]] = field(default_factory=dict)

    def __str__(self) -> str:
        lines = [f"Tool: {self.tool_name}  Score: {self.score:.2f}"]
        for check, (passed, note) in self.checks.items():
            marker = "✓" if passed else "✗"
            lines.append(f"  {marker} {check}: {note}")
        return "\n".join(lines)

    @property
    def passed(self) -> bool:
        return self.score >= READINESS_THRESHOLD


def _has_type_annotations(func: Callable) -> tuple[bool, str]:
    try:
        hints = get_type_hints(func)
    except Exception:
        return False, "Could not resolve type hints"
    sig = inspect.signature(func)
    params = [p for p in sig.parameters if p != "self"]
    if not params:
        return True, "No parameters"
    annotated = [p for p in params if p in hints]
    ratio = len(annotated) / len(params)
    return ratio >= 1.0, f"{len(annotated)}/{len(params)} parameters annotated"


def _has_return_annotation(func: Callable) -> tuple[bool, str]:
    try:
        hints = get_type_hints(func)
    except Exception:
        return False, "Could not resolve type hints"
    has_return = "return" in hints and hints["return"] is not type(None)
    return has_return, "return type present" if has_return else "missing return annotation"


def _docstring_length(func: Callable) -> tuple[bool, str]:
    doc = inspect.getdoc(func) or ""
    words = len(doc.split())
    ok = words >= 30
    return ok, f"{words} words (min 30)"


def _has_use_when(func: Callable) -> tuple[bool, str]:
    doc = (inspect.getdoc(func) or "").lower()
    found = "use when" in doc or "when to use" in doc
    return found, "USE WHEN section present" if found else "missing USE WHEN guidance"


def _has_never_use(func: Callable) -> tuple[bool, str]:
    doc = (inspect.getdoc(func) or "").lower()
    found = "never use" in doc or "do not use" in doc or "avoid" in doc
    return found, "anti-pattern section present" if found else "missing NEVER USE / anti-patterns"


def _has_args_section(func: Callable) -> tuple[bool, str]:
    doc = inspect.getdoc(func) or ""
    found = bool(re.search(r"Args?:", doc))
    return found, "Args section present" if found else "missing Args section"


def _has_returns_section(func: Callable) -> tuple[bool, str]:
    doc = inspect.getdoc(func) or ""
    found = bool(re.search(r"Returns?:", doc))
    return found, "Returns section present" if found else "missing Returns section"


def _has_domain_vocabulary(func: Callable) -> tuple[bool, str]:
    doc = (inspect.getdoc(func) or "").lower()
    matches = [term for term in DOMAIN_VOCABULARY if term in doc]
    ok = len(matches) >= 1
    detail = f"found: {matches}" if matches else f"none of {DOMAIN_VOCABULARY}"
    return ok, detail


def _no_vague_language(func: Callable) -> tuple[bool, str]:
    doc = (inspect.getdoc(func) or "").lower()
    vague = ["may", "sometimes", "depending on", "as needed", "if applicable"]
    found = [w for w in vague if w in doc]
    ok = len(found) == 0
    return ok, "no vague language" if ok else f"vague terms: {found}"


CHECKS: list[tuple[str, Callable, float]] = [
    # (check_name, check_fn, weight)
    ("type_annotations",    _has_type_annotations,  0.20),
    ("return_annotation",   _has_return_annotation, 0.10),
    ("docstring_length",    _docstring_length,       0.10),
    ("use_when",            _has_use_when,           0.15),
    ("never_use",           _has_never_use,          0.15),
    ("args_section",        _has_args_section,       0.10),
    ("returns_section",     _has_returns_section,    0.10),
    ("domain_vocabulary",   _has_domain_vocabulary,  0.05),
    ("no_vague_language",   _no_vague_language,      0.05),
]


def evaluate_tool(func: Callable) -> tuple[float, ReadinessReport]:
    """Return (score, report) for a candidate agent tool function."""
    results: dict[str, tuple[bool, str]] = {}
    weighted_score = 0.0

    for name, check_fn, weight in CHECKS:
        passed, note = check_fn(func)
        results[name] = (passed, note)
        if passed:
            weighted_score += weight

    report = ReadinessReport(
        tool_name=func.__name__,
        score=weighted_score,
        checks=results,
    )
    return weighted_score, report


def require_readiness(threshold: float = READINESS_THRESHOLD):
    """Decorator that raises at import time if a tool is not LLM-ready."""
    def decorator(func: Callable) -> Callable:
        score, report = evaluate_tool(func)
        if score < threshold:
            raise ValueError(
                f"Tool '{func.__name__}' is not LLM-ready "
                f"(score {score:.2f} < {threshold}):\n{report}"
            )
        return func
    return decorator


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from typing import Literal

    def bad_tool(name, type, properties):
        """Save an element."""
        ...

    @require_readiness()
    def good_tool(
        name: str,
        element_type: Literal["Application", "Data", "Business"],
        properties: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Persist a new ArchiMate element in the EA360 model.

        USE WHEN: The user wants to create a structured architecture component
        after validating its relationships against the TOGAF metamodel.

        NEVER USE FOR: Temporary notes, informal diagrams, or elements without
        clear stakeholder value.

        Args:
            name: Human-readable identifier (unique within its ArchiMate layer).
            element_type: ArchiMate 3.2 layer category — determines validation rules.
            properties: Mandatory fields vary by type:
                - Application: { "interfaces": list, "technology": str }
                - Data: { "sensitivity": "public|internal|confidential", "owner": str }
                - Business: { "process_owner": str, "kpi": str | None }

        Returns:
            dict: { "id": str, "status": "created|updated", "warnings": list[str] }
        """
        ...

    print("=== bad_tool ===")
    score, report = evaluate_tool(bad_tool)
    print(report)
    print(f"\nPassed gate: {report.passed}\n")

    print("=== good_tool ===")
    score, report = evaluate_tool(good_tool)
    print(report)
    print(f"\nPassed gate: {report.passed}")

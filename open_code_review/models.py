from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FileDiff:
    path: str
    old_path: Optional[str]  # for renames
    hunks: list[str]
    language: str = ""
    is_deleted: bool = False
    is_new: bool = False
    is_binary: bool = False

    def full_diff(self) -> str:
        return "\n".join(self.hunks)


@dataclass
class ReviewComment:
    file: str
    line: Optional[int]
    severity: str  # "error", "warning", "info", "suggestion"
    message: str
    suggestion: Optional[str] = None


@dataclass
class ReviewResult:
    comments: list[ReviewComment] = field(default_factory=list)
    summary: str = ""

    def has_errors(self) -> bool:
        return any(c.severity == "error" for c in self.comments)

    def __str__(self) -> str:
        lines = []
        if self.summary:
            lines.append(f"Summary: {self.summary}\n")
        for c in self.comments:
            loc = f"{c.file}:{c.line}" if c.line else c.file
            lines.append(f"[{c.severity.upper()}] {loc}: {c.message}")
            if c.suggestion:
                lines.append(f"  Suggestion: {c.suggestion}")
        return "\n".join(lines)

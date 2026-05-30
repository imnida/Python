"""Built-in deterministic review rules applied before LLM review."""

import re
from .models import FileDiff, ReviewComment


def _check_null_deref(f: FileDiff) -> list[ReviewComment]:
    comments = []
    for hunk in f.hunks:
        for i, line in enumerate(hunk.splitlines(), 1):
            if not line.startswith("+"):
                continue
            code = line[1:]
            # Potential null dereference patterns
            if re.search(r"\.\w+\s*\(.*None.*\)", code):
                comments.append(ReviewComment(
                    file=f.path, line=None, severity="warning",
                    message="Possible NoneType method call — consider a None check.",
                ))
    return comments


def _check_hardcoded_secrets(f: FileDiff) -> list[ReviewComment]:
    comments = []
    patterns = [
        (r'(?i)(password|passwd|secret|api_key|token)\s*=\s*["\'][^"\']{6,}["\']',
         "Hardcoded credential detected — use environment variables or a secrets manager."),
        (r'(?i)aws_access_key_id\s*=\s*["\']AKIA',
         "Hardcoded AWS access key detected."),
    ]
    for hunk in f.hunks:
        for line in hunk.splitlines():
            if not line.startswith("+"):
                continue
            code = line[1:]
            for pattern, msg in patterns:
                if re.search(pattern, code):
                    comments.append(ReviewComment(
                        file=f.path, line=None, severity="error", message=msg,
                    ))
    return comments


def _check_sql_injection(f: FileDiff) -> list[ReviewComment]:
    comments = []
    if f.language not in ("python", "javascript", "typescript", "php", "java"):
        return comments
    for hunk in f.hunks:
        for line in hunk.splitlines():
            if not line.startswith("+"):
                continue
            code = line[1:]
            if re.search(r'(execute|query)\s*\(\s*["\'].*%[sd].*["\']\s*%', code):
                comments.append(ReviewComment(
                    file=f.path, line=None, severity="error",
                    message="Possible SQL injection via string formatting — use parameterized queries.",
                ))
    return comments


def _check_xss(f: FileDiff) -> list[ReviewComment]:
    comments = []
    if f.language not in ("javascript", "typescript", "tsx", "jsx"):
        return comments
    for hunk in f.hunks:
        for line in hunk.splitlines():
            if not line.startswith("+"):
                continue
            code = line[1:]
            if "dangerouslySetInnerHTML" in code or "innerHTML" in code:
                comments.append(ReviewComment(
                    file=f.path, line=None, severity="warning",
                    message="Potential XSS via raw HTML insertion — sanitize content before rendering.",
                ))
    return comments


def apply_rules(files: list[FileDiff]) -> list[ReviewComment]:
    """Run all deterministic rules and return any findings."""
    all_comments: list[ReviewComment] = []
    rule_fns = [_check_null_deref, _check_hardcoded_secrets, _check_sql_injection, _check_xss]
    for f in files:
        for fn in rule_fns:
            all_comments.extend(fn(f))
    return all_comments

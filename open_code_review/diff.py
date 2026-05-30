import fnmatch
import re
import subprocess
from pathlib import Path
from typing import Optional

from .models import FileDiff

LANGUAGE_MAP = {
    ".py": "python", ".js": "javascript", ".ts": "typescript",
    ".tsx": "tsx", ".jsx": "jsx", ".go": "go", ".rs": "rust",
    ".java": "java", ".kt": "kotlin", ".swift": "swift",
    ".c": "c", ".cpp": "c++", ".h": "c", ".hpp": "c++",
    ".cs": "csharp", ".rb": "ruby", ".php": "php",
    ".sh": "bash", ".bash": "bash", ".zsh": "zsh",
    ".sql": "sql", ".yaml": "yaml", ".yml": "yaml",
    ".json": "json", ".toml": "toml", ".xml": "xml",
    ".html": "html", ".css": "css", ".scss": "scss",
    ".md": "markdown", ".tf": "terraform",
}


def _detect_language(path: str) -> str:
    ext = Path(path).suffix.lower()
    return LANGUAGE_MAP.get(ext, "")


def get_git_diff(
    base: Optional[str] = None,
    head: Optional[str] = None,
    staged: bool = False,
    commit: Optional[str] = None,
    cwd: Optional[str] = None,
) -> str:
    """Run git diff and return the raw diff string."""
    cmd = ["git", "diff", "--unified=5"]

    if commit:
        cmd += [f"{commit}^", commit]
    elif staged:
        cmd.append("--staged")
    elif base and head:
        cmd += [base, head]
    elif base:
        cmd += [base, "HEAD"]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"git diff failed: {result.stderr.strip()}")
    return result.stdout


def parse_diff(raw: str, excluded_patterns: list[str] | None = None) -> list[FileDiff]:
    """Parse a unified diff into a list of FileDiff objects."""
    excluded_patterns = excluded_patterns or []
    files: list[FileDiff] = []
    current: Optional[FileDiff] = None
    current_hunks: list[str] = []
    hunk_buf: list[str] = []

    def flush_hunk():
        if hunk_buf:
            current_hunks.append("\n".join(hunk_buf))
            hunk_buf.clear()

    def flush_file():
        nonlocal current, current_hunks
        if current is not None:
            flush_hunk()
            current.hunks = current_hunks[:]
            files.append(current)
        current_hunks = []

    for line in raw.splitlines():
        if line.startswith("diff --git"):
            flush_file()
            # Extract file path from "diff --git a/foo b/foo"
            m = re.match(r"diff --git a/(.*) b/(.*)", line)
            if m:
                old_path, new_path = m.group(1), m.group(2)
                current = FileDiff(
                    path=new_path,
                    old_path=old_path if old_path != new_path else None,
                    hunks=[],
                    language=_detect_language(new_path),
                )
            current_hunks = []
            hunk_buf = []
        elif line.startswith("new file mode"):
            if current:
                current.is_new = True
        elif line.startswith("deleted file mode"):
            if current:
                current.is_deleted = True
        elif line.startswith("Binary files"):
            if current:
                current.is_binary = True
        elif line.startswith("@@"):
            flush_hunk()
            hunk_buf = [line]
        elif current is not None and line.startswith(("+++", "---", "index ", "similarity")):
            pass  # skip metadata lines
        elif hunk_buf:
            hunk_buf.append(line)

    flush_file()

    # Filter excluded patterns and binary files
    result = []
    for f in files:
        if f.is_binary:
            continue
        excluded = any(
            fnmatch.fnmatch(f.path, pat) or fnmatch.fnmatch(Path(f.path).name, pat)
            for pat in excluded_patterns
        )
        if not excluded:
            result.append(f)
    return result


def bundle_files(files: list[FileDiff], max_tokens: int = 6000) -> list[list[FileDiff]]:
    """Group files into bundles for concurrent review, keeping related files together."""
    # Group by directory proximity
    groups: dict[str, list[FileDiff]] = {}
    for f in files:
        key = str(Path(f.path).parent)
        groups.setdefault(key, []).append(f)

    # Merge small groups and cap large ones
    bundles: list[list[FileDiff]] = []
    current_bundle: list[FileDiff] = []
    current_size = 0

    for group in groups.values():
        for f in group:
            size = sum(len(h) for h in f.hunks)
            if current_size + size > max_tokens * 4 and current_bundle:
                bundles.append(current_bundle)
                current_bundle = []
                current_size = 0
            current_bundle.append(f)
            current_size += size

    if current_bundle:
        bundles.append(current_bundle)
    return bundles

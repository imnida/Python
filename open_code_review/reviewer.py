import concurrent.futures
from typing import Optional

from .config import Config
from .diff import get_git_diff, parse_diff, bundle_files
from .llm import review_bundle
from .models import FileDiff, ReviewComment, ReviewResult
from .rules import apply_rules


def review(
    config: Config,
    base: Optional[str] = None,
    head: Optional[str] = None,
    staged: bool = False,
    commit: Optional[str] = None,
    raw_diff: Optional[str] = None,
    cwd: Optional[str] = None,
    verbose: bool = False,
) -> ReviewResult:
    """Run a full code review and return the aggregated result."""

    if raw_diff is None:
        raw_diff = get_git_diff(base=base, head=head, staged=staged, commit=commit, cwd=cwd)

    if not raw_diff.strip():
        return ReviewResult(summary="No changes to review.")

    files = parse_diff(raw_diff, excluded_patterns=config.review.excluded_patterns)
    if not files:
        return ReviewResult(summary="No reviewable files found in the diff.")

    if verbose:
        print(f"Reviewing {len(files)} file(s)...")

    # Deterministic rules first (fast, no LLM needed)
    rule_comments = apply_rules(files)

    # LLM review over file bundles (concurrent)
    bundles = bundle_files(files)
    if verbose:
        print(f"Sending {len(bundles)} bundle(s) to {config.llm.provider}/{config.llm.model}...")

    llm_summaries: list[str] = []
    llm_comments: list[ReviewComment] = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=config.review.concurrency) as pool:
        futures = {pool.submit(review_bundle, bundle, config): bundle for bundle in bundles}
        for future in concurrent.futures.as_completed(futures):
            summary, comments = future.result()
            if summary:
                llm_summaries.append(summary)
            llm_comments.extend(comments)

    all_comments = rule_comments + llm_comments
    combined_summary = " ".join(llm_summaries) if llm_summaries else ""

    return ReviewResult(comments=all_comments, summary=combined_summary)

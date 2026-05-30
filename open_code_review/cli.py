#!/usr/bin/env python3
"""open-code-review CLI — AI-powered code review for git diffs."""

import argparse
import json
import sys

from .config import Config, CONFIG_FILE
from .reviewer import review


def cmd_review(args: argparse.Namespace, config: Config) -> int:
    result = review(
        config=config,
        base=args.base,
        head=args.head,
        staged=args.staged,
        commit=args.commit,
        verbose=args.verbose,
    )

    if args.json:
        data = {
            "summary": result.summary,
            "comments": [
                {
                    "file": c.file,
                    "line": c.line,
                    "severity": c.severity,
                    "message": c.message,
                    "suggestion": c.suggestion,
                }
                for c in result.comments
            ],
        }
        print(json.dumps(data, indent=2))
    else:
        print(str(result))

    return 1 if result.has_errors() else 0


def cmd_config(args: argparse.Namespace, config: Config) -> int:
    if args.set:
        key, _, value = args.set.partition("=")
        key = key.strip()
        value = value.strip()
        if key == "llm.api_key":
            config.llm.api_key = value
        elif key == "llm.model":
            config.llm.model = value
        elif key == "llm.provider":
            config.llm.provider = value
        elif key == "llm.base_url":
            config.llm.base_url = value
        elif key == "llm.max_tokens":
            config.llm.max_tokens = int(value)
        elif key == "review.concurrency":
            config.review.concurrency = int(value)
        else:
            print(f"Unknown config key: {key}", file=sys.stderr)
            return 1
        config.save()
        print(f"Set {key} = {value!r}")
    elif args.show:
        print(f"Config file: {CONFIG_FILE}")
        print(f"  llm.provider:    {config.llm.provider}")
        print(f"  llm.model:       {config.llm.model}")
        print(f"  llm.api_key:     {'***' if config.llm.api_key else '(not set)'}")
        print(f"  llm.base_url:    {config.llm.base_url or '(default)'}")
        print(f"  llm.max_tokens:  {config.llm.max_tokens}")
        print(f"  review.concurrency: {config.review.concurrency}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ocr",
        description="AI-powered code review for git diffs",
    )
    sub = parser.add_subparsers(dest="command")

    # review subcommand
    rev = sub.add_parser("review", help="Review code changes")
    rev.add_argument("--base", metavar="REF", help="Base branch/commit for diff")
    rev.add_argument("--head", metavar="REF", help="Head branch/commit for diff")
    rev.add_argument("--staged", action="store_true", help="Review staged changes")
    rev.add_argument("--commit", metavar="SHA", help="Review a specific commit")
    rev.add_argument("--json", action="store_true", help="Output results as JSON")
    rev.add_argument("-v", "--verbose", action="store_true", help="Verbose output")

    # config subcommand
    cfg = sub.add_parser("config", help="Manage configuration")
    cfg_group = cfg.add_mutually_exclusive_group(required=True)
    cfg_group.add_argument("--set", metavar="KEY=VALUE", help="Set a config value")
    cfg_group.add_argument("--show", action="store_true", help="Show current config")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config = Config.load()

    if args.command == "review":
        if not config.llm.api_key:
            print(
                "Error: No API key configured.\n"
                "Set ANTHROPIC_API_KEY or OPENAI_API_KEY, or run:\n"
                "  ocr config --set llm.api_key=<your-key>",
                file=sys.stderr,
            )
            sys.exit(1)
        sys.exit(cmd_review(args, config))
    elif args.command == "config":
        sys.exit(cmd_config(args, config))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

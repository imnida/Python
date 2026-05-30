import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path


CONFIG_DIR = Path.home() / ".opencodereview"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_MODEL = "claude-sonnet-4-6"
DEFAULT_MAX_TOKENS = 4096
DEFAULT_CONCURRENCY = 4


@dataclass
class LLMConfig:
    provider: str = "anthropic"  # "anthropic" or "openai"
    model: str = DEFAULT_MODEL
    api_key: str = ""
    base_url: str = ""
    max_tokens: int = DEFAULT_MAX_TOKENS


@dataclass
class ReviewConfig:
    concurrency: int = DEFAULT_CONCURRENCY
    max_file_size: int = 100_000  # bytes
    excluded_patterns: list[str] = field(default_factory=lambda: [
        "*.lock", "*.min.js", "*.min.css", "*.pb.go", "*_generated.go",
        "vendor/*", "node_modules/*", "dist/*", "build/*",
    ])
    rules_file: str = ""


@dataclass
class Config:
    llm: LLMConfig = field(default_factory=LLMConfig)
    review: ReviewConfig = field(default_factory=ReviewConfig)

    @classmethod
    def load(cls) -> "Config":
        cfg = cls()
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                data = json.load(f)
            if "llm" in data:
                cfg.llm = LLMConfig(**data["llm"])
            if "review" in data:
                cfg.review = ReviewConfig(**data["review"])
        cfg._apply_env()
        return cfg

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(asdict(self), f, indent=2)

    def _apply_env(self) -> None:
        if key := os.environ.get("ANTHROPIC_API_KEY"):
            self.llm.api_key = key
            self.llm.provider = "anthropic"
        elif key := os.environ.get("OPENAI_API_KEY"):
            self.llm.api_key = key
            self.llm.provider = "openai"
        if model := os.environ.get("OCR_MODEL"):
            self.llm.model = model
        if base_url := os.environ.get("OCR_BASE_URL"):
            self.llm.base_url = base_url

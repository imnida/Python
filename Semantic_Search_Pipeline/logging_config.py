"""
Structured logging setup.
Call configure_logging() once at application entry point.
"""
import logging
import sys
from config import config


def configure_logging() -> logging.Logger:
    fmt = "%(asctime)s [%(levelname)s] %(name)s — %(message)s"
    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format=fmt,
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    # Silence noisy third-party loggers
    for noisy in ("urllib3", "requests", "py4j"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    return logging.getLogger("pipeline")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

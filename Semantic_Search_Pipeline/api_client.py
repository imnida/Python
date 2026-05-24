"""
Embedding API client with production-grade retry logic.

Key behaviours mirroring the article:
  - Exponential backoff on 429 / 5xx responses.
  - respect_retry_after_header honours the Retry-After header that OpenAI,
    Anthropic, and most embedding endpoints return on rate-limit responses.
  - Explicit response structure validation: a 200 with malformed JSON is
    caught before it poisons downstream data.
  - Mock mode (USE_MOCK_EMBEDDINGS=true) lets the pipeline run end-to-end
    without a real endpoint, using a deterministic hash-based embedding.
"""
from __future__ import annotations

import hashlib
import logging
import math
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import config
from logging_config import get_logger

logger = get_logger(__name__)

# Status codes that should trigger a retry
_RETRY_STATUSES = (429, 500, 502, 503, 504)


def build_session(
    retries: int = config.api_retries,
    backoff_factor: float = config.api_backoff_factor,
    statuses: tuple[int, ...] = _RETRY_STATUSES,
) -> requests.Session:
    """
    Return a requests.Session pre-configured with retry + backoff.
    Re-use one session per worker / thread — it pools connections.
    """
    session = requests.Session()
    retry_policy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=statuses,
        respect_retry_after_header=True,   # honours 429 Retry-After
        allowed_methods={"POST"},
        raise_on_status=False,             # we call raise_for_status() ourselves
    )
    adapter = HTTPAdapter(max_retries=retry_policy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    if config.embedding_api_key:
        session.headers.update({"Authorization": f"Bearer {config.embedding_api_key}"})

    logger.debug(
        "Session built: retries=%d backoff_factor=%.1f statuses=%s",
        retries,
        backoff_factor,
        statuses,
    )
    return session


# ---------------------------------------------------------------------------
# Real API call
# ---------------------------------------------------------------------------

def call_embedding_api(
    text: str,
    session: requests.Session,
    endpoint: str = config.embedding_endpoint,
    timeout: int = config.api_timeout,
) -> list[float]:
    """
    POST text to the embedding endpoint and return the float vector.
    Raises ValueError when the API returns 200 with a malformed body —
    a surprisingly common production failure mode.
    """
    response = session.post(
        endpoint,
        json={"text": text},
        timeout=timeout,
    )
    response.raise_for_status()
    result = response.json()

    if "embedding" not in result or not isinstance(result["embedding"], list):
        raise ValueError(
            f"Unexpected API response structure — keys: {list(result.keys())}"
        )

    embedding: list[float] = result["embedding"]
    logger.debug("Received embedding dim=%d for text[:%d]", len(embedding), 40)
    return embedding


# ---------------------------------------------------------------------------
# Mock embedding (no external dependency, deterministic, L2-normalised)
# ---------------------------------------------------------------------------

def mock_embedding(text: str, dim: int = config.embedding_dim) -> list[float]:
    """
    Deterministic pseudo-embedding derived from the text's SHA-256 hash.

    Properties:
      - Same text always produces the same vector (reproducible).
      - Different texts produce different vectors (no collisions in practice).
      - L2-normalised, so cosine similarity == dot product (matches most
        production vector stores configured for inner-product search).

    Not semantically meaningful — use only for testing pipeline plumbing.
    """
    digest = hashlib.sha256(text.encode()).digest()
    # Expand the 32-byte digest to `dim` floats using cycling + mixing
    raw: list[float] = []
    seed = digest
    while len(raw) < dim:
        seed = hashlib.sha256(seed).digest()
        raw.extend(b / 255.0 for b in seed)
    raw = raw[:dim]

    # L2 normalise
    magnitude = math.sqrt(sum(v * v for v in raw))
    if magnitude == 0:
        return [0.0] * dim
    return [v / magnitude for v in raw]


# ---------------------------------------------------------------------------
# Unified entry point
# ---------------------------------------------------------------------------

def get_embedding(
    text: str,
    session: Optional[requests.Session] = None,
) -> list[float]:
    """
    Return an embedding for *text*.
    Uses the mock when USE_MOCK_EMBEDDINGS=true (default), otherwise calls
    the real API endpoint.
    """
    if not text or not text.strip():
        logger.warning("get_embedding called with empty text — returning zero vector")
        return [0.0] * config.embedding_dim

    if config.use_mock_embeddings:
        return mock_embedding(text)

    if session is None:
        session = build_session()
    return call_embedding_api(text, session)

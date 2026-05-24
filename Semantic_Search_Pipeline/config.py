"""
Pipeline configuration loaded from environment variables with safe defaults.
All tuneable constants live here so operators can override without code changes.
"""
import os
from dataclasses import dataclass, field


@dataclass
class PipelineConfig:
    # --- chunking ---
    chunk_days: int = int(os.getenv("CHUNK_DAYS", "7"))

    # --- embedding API ---
    embedding_endpoint: str = os.getenv(
        "EMBEDDING_ENDPOINT", "https://your-embedding-endpoint/embed"
    )
    embedding_api_key: str = os.getenv("EMBEDDING_API_KEY", "")
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "128"))
    api_timeout: int = int(os.getenv("API_TIMEOUT", "30"))
    api_retries: int = int(os.getenv("API_RETRIES", "3"))
    api_backoff_factor: float = float(os.getenv("API_BACKOFF_FACTOR", "2.0"))

    # --- spark ---
    spark_app_name: str = os.getenv("SPARK_APP_NAME", "SemanticSearchPipeline")
    spark_master: str = os.getenv("SPARK_MASTER", "local[*]")

    # --- storage ---
    output_path: str = os.getenv("OUTPUT_PATH", "/tmp/semantic_search/embeddings")
    vector_store_path: str = os.getenv("VECTOR_STORE_PATH", "/tmp/semantic_search/vectors")

    # --- observability ---
    enable_profiling: bool = os.getenv("ENABLE_PROFILING", "false").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # --- demo / testing ---
    use_mock_embeddings: bool = os.getenv("USE_MOCK_EMBEDDINGS", "true").lower() == "true"


# Module-level singleton — import this everywhere
config = PipelineConfig()

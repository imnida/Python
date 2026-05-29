from dataclasses import dataclass


@dataclass
class SharedRideAttributes:
    """Variant-specific fields for shared (pooled) rides."""

    passenger_count: int
    pooling_score: float

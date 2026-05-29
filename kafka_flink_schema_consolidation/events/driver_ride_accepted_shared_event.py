from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base_ride_event import BaseRideEvent


@dataclass
class DriverRideAcceptedSharedEvent(BaseRideEvent):
    """Emitted when a driver accepts a shared (pooled) ride request."""

    passenger_count: int
    pooling_score: float

    @classmethod
    def from_map(cls, raw: Dict[str, Any]) -> DriverRideAcceptedSharedEvent:
        return cls(
            **cls._base_kwargs(raw),
            passenger_count=int(raw.get("passengerCount", 1)),
            pooling_score=float(raw.get("poolingScore", 0.0)),
        )

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base_ride_event import BaseRideEvent


@dataclass
class DriverRideCompletedSharedEvent(BaseRideEvent):
    """Emitted when a shared ride completes."""

    passenger_count: int
    pooling_score: float
    fare_amount: float
    duration_minutes: int
    distance_km: float

    @classmethod
    def from_map(cls, raw: Dict[str, Any]) -> DriverRideCompletedSharedEvent:
        return cls(
            **cls._base_kwargs(raw),
            passenger_count=int(raw.get("passengerCount", 1)),
            pooling_score=float(raw.get("poolingScore", 0.0)),
            fare_amount=float(raw.get("fareAmount", 0.0)),
            duration_minutes=int(raw.get("durationMinutes", 0)),
            distance_km=float(raw.get("distanceKm", 0.0)),
        )

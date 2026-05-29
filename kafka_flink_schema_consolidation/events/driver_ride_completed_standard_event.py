from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base_ride_event import BaseRideEvent


@dataclass
class DriverRideCompletedStandardEvent(BaseRideEvent):
    """Emitted when a standard ride completes.

    fare_amount, duration_minutes, and distance_km are always populated.
    """

    vehicle_class: str
    surge_multiplier: float
    fare_amount: float
    duration_minutes: int
    distance_km: float

    @classmethod
    def from_map(cls, raw: Dict[str, Any]) -> DriverRideCompletedStandardEvent:
        return cls(
            **cls._base_kwargs(raw),
            vehicle_class=str(raw.get("vehicleClass", "UberX")),
            surge_multiplier=float(raw.get("surgeMultiplier", 1.0)),
            fare_amount=float(raw.get("fareAmount", 0.0)),
            duration_minutes=int(raw.get("durationMinutes", 0)),
            distance_km=float(raw.get("distanceKm", 0.0)),
        )

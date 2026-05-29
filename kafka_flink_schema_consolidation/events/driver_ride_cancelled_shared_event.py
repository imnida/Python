from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base_ride_event import BaseRideEvent


@dataclass
class DriverRideCancelledSharedEvent(BaseRideEvent):
    """Emitted when a shared ride is cancelled."""

    passenger_count: int
    pooling_score: float
    cancellation_reason: str

    @classmethod
    def from_map(cls, raw: Dict[str, Any]) -> DriverRideCancelledSharedEvent:
        return cls(
            **cls._base_kwargs(raw),
            passenger_count=int(raw.get("passengerCount", 1)),
            pooling_score=float(raw.get("poolingScore", 0.0)),
            cancellation_reason=str(raw.get("cancellationReason", "")),
        )

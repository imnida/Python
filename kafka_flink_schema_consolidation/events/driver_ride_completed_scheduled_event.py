from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base_ride_event import BaseRideEvent


@dataclass
class DriverRideCompletedScheduledEvent(BaseRideEvent):
    """Emitted when a scheduled ride completes."""

    scheduled_time: int
    advance_booking_minutes: int
    fare_amount: float
    duration_minutes: int
    distance_km: float

    @classmethod
    def from_map(cls, raw: Dict[str, Any]) -> DriverRideCompletedScheduledEvent:
        return cls(
            **cls._base_kwargs(raw),
            scheduled_time=int(raw.get("scheduledTime", 0)),
            advance_booking_minutes=int(raw.get("advanceBookingMinutes", 0)),
            fare_amount=float(raw.get("fareAmount", 0.0)),
            duration_minutes=int(raw.get("durationMinutes", 0)),
            distance_km=float(raw.get("distanceKm", 0.0)),
        )

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base_ride_event import BaseRideEvent


@dataclass
class DriverRideAcceptedScheduledEvent(BaseRideEvent):
    """Emitted when a driver accepts a pre-scheduled ride request."""

    scheduled_time: int
    advance_booking_minutes: int

    @classmethod
    def from_map(cls, raw: Dict[str, Any]) -> DriverRideAcceptedScheduledEvent:
        return cls(
            **cls._base_kwargs(raw),
            scheduled_time=int(raw.get("scheduledTime", 0)),
            advance_booking_minutes=int(raw.get("advanceBookingMinutes", 0)),
        )

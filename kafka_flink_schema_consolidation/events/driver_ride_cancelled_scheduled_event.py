from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base_ride_event import BaseRideEvent


@dataclass
class DriverRideCancelledScheduledEvent(BaseRideEvent):
    """Emitted when a scheduled ride is cancelled."""

    scheduled_time: int
    advance_booking_minutes: int
    cancellation_reason: str

    @classmethod
    def from_map(cls, raw: Dict[str, Any]) -> DriverRideCancelledScheduledEvent:
        return cls(
            **cls._base_kwargs(raw),
            scheduled_time=int(raw.get("scheduledTime", 0)),
            advance_booking_minutes=int(raw.get("advanceBookingMinutes", 0)),
            cancellation_reason=str(raw.get("cancellationReason", "")),
        )

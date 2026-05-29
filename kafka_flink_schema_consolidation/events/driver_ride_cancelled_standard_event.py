from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base_ride_event import BaseRideEvent


@dataclass
class DriverRideCancelledStandardEvent(BaseRideEvent):
    """Emitted when a standard ride is cancelled before pickup.

    cancellation_reason is always populated.
    """

    vehicle_class: str
    surge_multiplier: float
    cancellation_reason: str

    @classmethod
    def from_map(cls, raw: Dict[str, Any]) -> DriverRideCancelledStandardEvent:
        return cls(
            **cls._base_kwargs(raw),
            vehicle_class=str(raw.get("vehicleClass", "UberX")),
            surge_multiplier=float(raw.get("surgeMultiplier", 1.0)),
            cancellation_reason=str(raw.get("cancellationReason", "")),
        )

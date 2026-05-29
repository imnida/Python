from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from .base_ride_event import BaseRideEvent


@dataclass
class DriverRideAcceptedStandardEvent(BaseRideEvent):
    """Emitted when a driver accepts a standard (single-passenger) ride request."""

    vehicle_class: str
    surge_multiplier: float

    @classmethod
    def from_map(cls, raw: Dict[str, Any]) -> DriverRideAcceptedStandardEvent:
        return cls(
            **cls._base_kwargs(raw),
            vehicle_class=str(raw.get("vehicleClass", "UberX")),
            surge_multiplier=float(raw.get("surgeMultiplier", 1.0)),
        )

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class BaseRideEvent:
    """Fields shared across all 12 ride-event variants.

    The 80-95 % structural overlap across the fragmented schemas is encoded
    here once; subclasses add only variant-specific fields.
    """

    event_time: int
    driver_id: str
    ride_id: str
    city_id: str
    pickup_lat: float
    pickup_lng: float
    estimated_duration_minutes: int
    estimated_fare: float

    @classmethod
    def _base_kwargs(cls, raw: Dict[str, Any]) -> dict:
        return {
            "event_time": int(raw.get("eventTime", 0)),
            "driver_id": str(raw.get("driverId", "")),
            "ride_id": str(raw.get("rideId", "")),
            "city_id": str(raw.get("cityId", "")),
            "pickup_lat": float(raw.get("pickupLat", 0.0)),
            "pickup_lng": float(raw.get("pickupLng", 0.0)),
            "estimated_duration_minutes": int(raw.get("estimatedDurationMinutes", 0)),
            "estimated_fare": float(raw.get("estimatedFare", 0.0)),
        }

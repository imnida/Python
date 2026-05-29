from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ..model.event_type import EventType
from ..model.ride_type import RideType
from .standard_ride_attributes import StandardRideAttributes
from .shared_ride_attributes import SharedRideAttributes
from .scheduled_ride_attributes import ScheduledRideAttributes


@dataclass
class DriverRideActivityRecord:
    """Single consolidated output record representing any of the 12 ride-event variants.

    Always-populated discriminator fields (event_type, ride_type) identify the variant.
    Exactly one of the three ride-attribute blocks will be non-None per record.
    Completion / cancellation fields are populated only for the matching event type.
    """

    event_time: int
    driver_id: str
    ride_id: str
    city_id: str
    pickup_lat: float
    pickup_lng: float
    event_type: EventType
    ride_type: RideType

    # Present for ACCEPTED and STARTED; None for COMPLETED and CANCELLED
    estimated_duration_minutes: Optional[int] = None
    estimated_fare: Optional[float] = None

    # Present only for COMPLETED events
    fare_amount: Optional[float] = None
    duration_minutes: Optional[int] = None
    distance_km: Optional[float] = None

    # Present only for CANCELLED events
    cancellation_reason: Optional[str] = None

    # Exactly one block is non-None per record
    standard_ride_attributes: Optional[StandardRideAttributes] = None
    shared_ride_attributes: Optional[SharedRideAttributes] = None
    scheduled_ride_attributes: Optional[ScheduledRideAttributes] = None

from dataclasses import dataclass


@dataclass
class ScheduledRideAttributes:
    """Variant-specific fields for pre-scheduled rides."""

    scheduled_time: int
    advance_booking_minutes: int

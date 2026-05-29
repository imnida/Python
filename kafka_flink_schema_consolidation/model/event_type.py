from enum import Enum


class EventType(str, Enum):
    """Discriminator identifying the type of driver ride-activity event.

    Together with RideType, replaces the need for separate schemas per
    event-type / ride-type combination.
    """

    # fareAmount, durationMinutes, distanceKm, and cancellationReason will be None
    ACCEPTED = "ACCEPTED"

    # fareAmount, durationMinutes, distanceKm, and cancellationReason will be None
    STARTED = "STARTED"

    # fareAmount, durationMinutes, and distanceKm will be populated;
    # cancellationReason will be None
    COMPLETED = "COMPLETED"

    # cancellationReason will be populated;
    # fareAmount, durationMinutes, and distanceKm will be None
    CANCELLED = "CANCELLED"

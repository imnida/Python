from enum import Enum


class RideType(str, Enum):
    """Discriminator identifying the ride product type.

    Used alongside EventType to fully identify the variant of each record so
    that a single consolidated schema can represent all 12 combinations.
    """

    # sharedRideAttributes and scheduledRideAttributes will be None
    STANDARD = "STANDARD"

    # sharedRideAttributes will be populated; scheduledRideAttributes will be None
    SHARED = "SHARED"

    # scheduledRideAttributes will be populated; sharedRideAttributes will be None
    SCHEDULED = "SCHEDULED"

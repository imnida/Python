from dataclasses import dataclass


@dataclass
class StandardRideAttributes:
    """Variant-specific fields for single-passenger standard rides."""

    vehicle_class: str
    surge_multiplier: float

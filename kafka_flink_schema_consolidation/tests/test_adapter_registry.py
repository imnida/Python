"""Tests for AdapterRegistry — mirrors AdapterRegistryTest.java."""
import pytest

from ..adapter.adapter_registry import AdapterRegistry
from ..model.event_type import EventType
from ..model.ride_type import RideType


def _base_raw() -> dict:
    return {
        "eventTime": 1_700_000_000,
        "driverId": "d-001",
        "rideId": "r-001",
        "cityId": "nyc",
        "pickupLat": 40.71,
        "pickupLng": -74.00,
        "estimatedDurationMinutes": 15,
        "estimatedFare": 12.50,
    }


def _raw_for(event_type: EventType, ride_type: RideType) -> dict:
    raw = _base_raw()
    raw["eventType"] = event_type.value
    raw["rideType"] = ride_type.value

    if ride_type == RideType.STANDARD:
        raw.update(vehicleClass="UberX", surgeMultiplier=1.5)
    elif ride_type == RideType.SHARED:
        raw.update(passengerCount=2, poolingScore=0.9)
    elif ride_type == RideType.SCHEDULED:
        raw.update(scheduledTime=1_700_003_600, advanceBookingMinutes=45)

    if event_type == EventType.COMPLETED:
        raw.update(fareAmount=18.0, durationMinutes=20, distanceKm=7.5)
    elif event_type == EventType.CANCELLED:
        raw.update(cancellationReason="DRIVER_NO_SHOW")

    return raw


class TestAdapterRegistry:
    def test_all_twelve_combinations_registered(self):
        registry = AdapterRegistry.with_all_adapters()
        for event_type in EventType:
            for ride_type in RideType:
                record = registry.adapt("org", _raw_for(event_type, ride_type), event_type, ride_type)
                assert record.event_type == event_type
                assert record.ride_type == ride_type

    def test_unknown_combination_raises_key_error(self):
        empty_registry = AdapterRegistry()
        with pytest.raises(KeyError):
            empty_registry.adapt("org", _base_raw(), EventType.ACCEPTED, RideType.STANDARD)

    def test_standard_ride_accepted_populates_attribute_block(self):
        registry = AdapterRegistry.with_all_adapters()
        raw = _raw_for(EventType.ACCEPTED, RideType.STANDARD)
        record = registry.adapt("org", raw, EventType.ACCEPTED, RideType.STANDARD)

        assert record.standard_ride_attributes is not None
        assert record.standard_ride_attributes.vehicle_class == "UberX"
        assert record.standard_ride_attributes.surge_multiplier == 1.5
        assert record.shared_ride_attributes is None
        assert record.scheduled_ride_attributes is None

    def test_shared_ride_accepted_populates_attribute_block(self):
        registry = AdapterRegistry.with_all_adapters()
        raw = _raw_for(EventType.ACCEPTED, RideType.SHARED)
        record = registry.adapt("org", raw, EventType.ACCEPTED, RideType.SHARED)

        assert record.shared_ride_attributes is not None
        assert record.shared_ride_attributes.passenger_count == 2
        assert record.shared_ride_attributes.pooling_score == 0.9
        assert record.standard_ride_attributes is None
        assert record.scheduled_ride_attributes is None

    def test_scheduled_ride_accepted_populates_attribute_block(self):
        registry = AdapterRegistry.with_all_adapters()
        raw = _raw_for(EventType.ACCEPTED, RideType.SCHEDULED)
        record = registry.adapt("org", raw, EventType.ACCEPTED, RideType.SCHEDULED)

        assert record.scheduled_ride_attributes is not None
        assert record.scheduled_ride_attributes.scheduled_time == 1_700_003_600
        assert record.scheduled_ride_attributes.advance_booking_minutes == 45
        assert record.standard_ride_attributes is None
        assert record.shared_ride_attributes is None

    def test_completed_ride_populates_fare_fields(self):
        registry = AdapterRegistry.with_all_adapters()
        raw = _raw_for(EventType.COMPLETED, RideType.STANDARD)
        record = registry.adapt("org", raw, EventType.COMPLETED, RideType.STANDARD)

        assert record.fare_amount == 18.0
        assert record.duration_minutes == 20
        assert record.distance_km == 7.5
        assert record.cancellation_reason is None

    def test_cancelled_ride_populates_cancellation_reason(self):
        registry = AdapterRegistry.with_all_adapters()
        raw = _raw_for(EventType.CANCELLED, RideType.STANDARD)
        record = registry.adapt("org", raw, EventType.CANCELLED, RideType.STANDARD)

        assert record.cancellation_reason == "DRIVER_NO_SHOW"
        assert record.fare_amount is None
        assert record.duration_minutes is None
        assert record.distance_km is None

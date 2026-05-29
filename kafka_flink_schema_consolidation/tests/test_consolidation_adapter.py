"""Tests for ConsolidationAdapter — JSON parsing and discriminator resolution."""
import json
import pytest

from ..adapter.consolidation_adapter import ConsolidationAdapter
from ..model.event_type import EventType
from ..model.ride_type import RideType


def _make_json(**kwargs) -> str:
    base = {
        "eventTime": 1_700_000_000,
        "driverId": "d-007",
        "rideId": "r-099",
        "cityId": "sfo",
        "pickupLat": 37.77,
        "pickupLng": -122.42,
        "estimatedDurationMinutes": 10,
        "estimatedFare": 9.0,
        "vehicleClass": "UberX",
        "surgeMultiplier": 1.0,
    }
    base.update(kwargs)
    return json.dumps(base)


class TestConsolidationAdapter:
    def setup_method(self):
        self.adapter = ConsolidationAdapter()

    def test_parses_standard_accepted(self):
        record = self.adapter.map("org", _make_json(eventType="ACCEPTED", rideType="STANDARD"))
        assert record.event_type == EventType.ACCEPTED
        assert record.ride_type == RideType.STANDARD
        assert record.driver_id == "d-007"

    def test_parses_shared_completed(self):
        payload = _make_json(
            eventType="COMPLETED",
            rideType="SHARED",
            passengerCount=3,
            poolingScore=0.75,
            fareAmount=11.0,
            durationMinutes=14,
            distanceKm=5.2,
        )
        record = self.adapter.map("org", payload)
        assert record.event_type == EventType.COMPLETED
        assert record.ride_type == RideType.SHARED
        assert record.fare_amount == 11.0
        assert record.shared_ride_attributes is not None
        assert record.shared_ride_attributes.passenger_count == 3

    def test_unknown_event_type_defaults_to_accepted(self):
        record = self.adapter.map("org", _make_json(eventType="MYSTERY", rideType="STANDARD"))
        assert record.event_type == EventType.ACCEPTED

    def test_unknown_ride_type_defaults_to_standard(self):
        record = self.adapter.map("org", _make_json(eventType="ACCEPTED", rideType="MYSTERY"))
        assert record.ride_type == RideType.STANDARD

    def test_invalid_json_raises_value_error(self):
        with pytest.raises(ValueError):
            self.adapter.map("org", "not-valid-json{{{")

    def test_scheduled_cancelled_with_reason(self):
        payload = _make_json(
            eventType="CANCELLED",
            rideType="SCHEDULED",
            scheduledTime=1_700_003_600,
            advanceBookingMinutes=30,
            cancellationReason="WEATHER",
        )
        record = self.adapter.map("org", payload)
        assert record.event_type == EventType.CANCELLED
        assert record.ride_type == RideType.SCHEDULED
        assert record.cancellation_reason == "WEATHER"
        assert record.scheduled_ride_attributes is not None
        assert record.scheduled_ride_attributes.advance_booking_minutes == 30

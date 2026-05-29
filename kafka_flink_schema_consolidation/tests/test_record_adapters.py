"""Unit tests for individual RecordAdapter implementations."""
import pytest

from ..adapter.standard_ride_accepted_adapter import StandardRideAcceptedAdapter
from ..adapter.standard_ride_completed_adapter import StandardRideCompletedAdapter
from ..adapter.standard_ride_cancelled_adapter import StandardRideCancelledAdapter
from ..adapter.shared_ride_accepted_adapter import SharedRideAcceptedAdapter
from ..adapter.shared_ride_completed_adapter import SharedRideCompletedAdapter
from ..adapter.scheduled_ride_accepted_adapter import ScheduledRideAcceptedAdapter
from ..adapter.scheduled_ride_cancelled_adapter import ScheduledRideCancelledAdapter

from ..events.driver_ride_accepted_standard_event import DriverRideAcceptedStandardEvent
from ..events.driver_ride_completed_standard_event import DriverRideCompletedStandardEvent
from ..events.driver_ride_cancelled_standard_event import DriverRideCancelledStandardEvent
from ..events.driver_ride_accepted_shared_event import DriverRideAcceptedSharedEvent
from ..events.driver_ride_completed_shared_event import DriverRideCompletedSharedEvent
from ..events.driver_ride_accepted_scheduled_event import DriverRideAcceptedScheduledEvent
from ..events.driver_ride_cancelled_scheduled_event import DriverRideCancelledScheduledEvent

from ..model.event_type import EventType
from ..model.ride_type import RideType


def _make_standard_accepted() -> DriverRideAcceptedStandardEvent:
    return DriverRideAcceptedStandardEvent(
        event_time=1_700_000_000,
        driver_id="d-001",
        ride_id="r-001",
        city_id="nyc",
        pickup_lat=40.71,
        pickup_lng=-74.00,
        estimated_duration_minutes=15,
        estimated_fare=12.50,
        vehicle_class="UberX",
        surge_multiplier=1.3,
    )


def _make_standard_completed() -> DriverRideCompletedStandardEvent:
    return DriverRideCompletedStandardEvent(
        event_time=1_700_001_000,
        driver_id="d-001",
        ride_id="r-001",
        city_id="nyc",
        pickup_lat=40.71,
        pickup_lng=-74.00,
        estimated_duration_minutes=15,
        estimated_fare=12.50,
        vehicle_class="UberX",
        surge_multiplier=1.3,
        fare_amount=14.60,
        duration_minutes=18,
        distance_km=6.2,
    )


def _make_standard_cancelled() -> DriverRideCancelledStandardEvent:
    return DriverRideCancelledStandardEvent(
        event_time=1_700_000_500,
        driver_id="d-001",
        ride_id="r-001",
        city_id="nyc",
        pickup_lat=40.71,
        pickup_lng=-74.00,
        estimated_duration_minutes=15,
        estimated_fare=12.50,
        vehicle_class="UberX",
        surge_multiplier=1.0,
        cancellation_reason="DRIVER_NO_SHOW",
    )


class TestStandardRideAcceptedAdapter:
    def test_sets_discriminators(self):
        record = StandardRideAcceptedAdapter().adapt("org", _make_standard_accepted())
        assert record.event_type == EventType.ACCEPTED
        assert record.ride_type == RideType.STANDARD

    def test_copies_base_fields(self):
        event = _make_standard_accepted()
        record = StandardRideAcceptedAdapter().adapt("org", event)
        assert record.event_time == event.event_time
        assert record.driver_id == event.driver_id
        assert record.ride_id == event.ride_id

    def test_populates_standard_attributes_only(self):
        record = StandardRideAcceptedAdapter().adapt("org", _make_standard_accepted())
        assert record.standard_ride_attributes is not None
        assert record.standard_ride_attributes.vehicle_class == "UberX"
        assert record.standard_ride_attributes.surge_multiplier == 1.3
        assert record.shared_ride_attributes is None
        assert record.scheduled_ride_attributes is None

    def test_completion_fields_are_none(self):
        record = StandardRideAcceptedAdapter().adapt("org", _make_standard_accepted())
        assert record.fare_amount is None
        assert record.duration_minutes is None
        assert record.distance_km is None
        assert record.cancellation_reason is None


class TestStandardRideCompletedAdapter:
    def test_populates_fare_fields(self):
        record = StandardRideCompletedAdapter().adapt("org", _make_standard_completed())
        assert record.fare_amount == 14.60
        assert record.duration_minutes == 18
        assert record.distance_km == 6.2

    def test_completion_fields_null_for_accepted(self):
        record = StandardRideAcceptedAdapter().adapt("org", _make_standard_accepted())
        assert record.fare_amount is None


class TestStandardRideCancelledAdapter:
    def test_populates_cancellation_reason(self):
        record = StandardRideCancelledAdapter().adapt("org", _make_standard_cancelled())
        assert record.cancellation_reason == "DRIVER_NO_SHOW"
        assert record.fare_amount is None


class TestSharedRideAcceptedAdapter:
    def test_populates_shared_attributes(self):
        event = DriverRideAcceptedSharedEvent(
            event_time=1_700_000_000,
            driver_id="d-002",
            ride_id="r-002",
            city_id="la",
            pickup_lat=34.05,
            pickup_lng=-118.24,
            estimated_duration_minutes=12,
            estimated_fare=10.0,
            passenger_count=3,
            pooling_score=0.88,
        )
        record = SharedRideAcceptedAdapter().adapt("org", event)
        assert record.ride_type == RideType.SHARED
        assert record.shared_ride_attributes is not None
        assert record.shared_ride_attributes.passenger_count == 3
        assert record.shared_ride_attributes.pooling_score == 0.88
        assert record.standard_ride_attributes is None
        assert record.scheduled_ride_attributes is None


class TestSharedRideCompletedAdapter:
    def test_populates_fare_and_shared_attributes(self):
        event = DriverRideCompletedSharedEvent(
            event_time=1_700_001_000,
            driver_id="d-002",
            ride_id="r-002",
            city_id="la",
            pickup_lat=34.05,
            pickup_lng=-118.24,
            estimated_duration_minutes=12,
            estimated_fare=10.0,
            passenger_count=2,
            pooling_score=0.70,
            fare_amount=9.50,
            duration_minutes=15,
            distance_km=5.0,
        )
        record = SharedRideCompletedAdapter().adapt("org", event)
        assert record.fare_amount == 9.50
        assert record.shared_ride_attributes.passenger_count == 2


class TestScheduledRideAcceptedAdapter:
    def test_populates_scheduled_attributes(self):
        event = DriverRideAcceptedScheduledEvent(
            event_time=1_700_000_000,
            driver_id="d-003",
            ride_id="r-003",
            city_id="chi",
            pickup_lat=41.88,
            pickup_lng=-87.63,
            estimated_duration_minutes=25,
            estimated_fare=20.0,
            scheduled_time=1_700_003_600,
            advance_booking_minutes=60,
        )
        record = ScheduledRideAcceptedAdapter().adapt("org", event)
        assert record.ride_type == RideType.SCHEDULED
        assert record.scheduled_ride_attributes is not None
        assert record.scheduled_ride_attributes.scheduled_time == 1_700_003_600
        assert record.scheduled_ride_attributes.advance_booking_minutes == 60
        assert record.standard_ride_attributes is None
        assert record.shared_ride_attributes is None


class TestScheduledRideCancelledAdapter:
    def test_populates_cancellation_and_scheduled_attributes(self):
        event = DriverRideCancelledScheduledEvent(
            event_time=1_700_000_900,
            driver_id="d-003",
            ride_id="r-003",
            city_id="chi",
            pickup_lat=41.88,
            pickup_lng=-87.63,
            estimated_duration_minutes=25,
            estimated_fare=20.0,
            scheduled_time=1_700_003_600,
            advance_booking_minutes=60,
            cancellation_reason="WEATHER",
        )
        record = ScheduledRideCancelledAdapter().adapt("org", event)
        assert record.event_type == EventType.CANCELLED
        assert record.cancellation_reason == "WEATHER"
        assert record.scheduled_ride_attributes.advance_booking_minutes == 60

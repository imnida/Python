from ..events.driver_ride_started_scheduled_event import DriverRideStartedScheduledEvent
from ..model.event_type import EventType
from ..model.ride_type import RideType
from ..schema.driver_ride_activity_record import DriverRideActivityRecord
from ..schema.scheduled_ride_attributes import ScheduledRideAttributes


class ScheduledRideStartedAdapter:
    """No framework dependency. Pure transformation logic."""

    def adapt(self, org_id: str, event: DriverRideStartedScheduledEvent) -> DriverRideActivityRecord:
        return DriverRideActivityRecord(
            event_time=event.event_time,
            driver_id=event.driver_id,
            ride_id=event.ride_id,
            city_id=event.city_id,
            pickup_lat=event.pickup_lat,
            pickup_lng=event.pickup_lng,
            event_type=EventType.STARTED,
            ride_type=RideType.SCHEDULED,
            estimated_duration_minutes=event.estimated_duration_minutes,
            estimated_fare=event.estimated_fare,
            scheduled_ride_attributes=ScheduledRideAttributes(
                scheduled_time=event.scheduled_time,
                advance_booking_minutes=event.advance_booking_minutes,
            ),
        )

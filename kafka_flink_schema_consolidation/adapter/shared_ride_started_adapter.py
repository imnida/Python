from ..events.driver_ride_started_shared_event import DriverRideStartedSharedEvent
from ..model.event_type import EventType
from ..model.ride_type import RideType
from ..schema.driver_ride_activity_record import DriverRideActivityRecord
from ..schema.shared_ride_attributes import SharedRideAttributes


class SharedRideStartedAdapter:
    """No framework dependency. Pure transformation logic."""

    def adapt(self, org_id: str, event: DriverRideStartedSharedEvent) -> DriverRideActivityRecord:
        return DriverRideActivityRecord(
            event_time=event.event_time,
            driver_id=event.driver_id,
            ride_id=event.ride_id,
            city_id=event.city_id,
            pickup_lat=event.pickup_lat,
            pickup_lng=event.pickup_lng,
            event_type=EventType.STARTED,
            ride_type=RideType.SHARED,
            estimated_duration_minutes=event.estimated_duration_minutes,
            estimated_fare=event.estimated_fare,
            shared_ride_attributes=SharedRideAttributes(
                passenger_count=event.passenger_count,
                pooling_score=event.pooling_score,
            ),
        )

from ..events.driver_ride_completed_shared_event import DriverRideCompletedSharedEvent
from ..model.event_type import EventType
from ..model.ride_type import RideType
from ..schema.driver_ride_activity_record import DriverRideActivityRecord
from ..schema.shared_ride_attributes import SharedRideAttributes


class SharedRideCompletedAdapter:
    """No framework dependency. Pure transformation logic."""

    def adapt(self, org_id: str, event: DriverRideCompletedSharedEvent) -> DriverRideActivityRecord:
        return DriverRideActivityRecord(
            event_time=event.event_time,
            driver_id=event.driver_id,
            ride_id=event.ride_id,
            city_id=event.city_id,
            pickup_lat=event.pickup_lat,
            pickup_lng=event.pickup_lng,
            event_type=EventType.COMPLETED,
            ride_type=RideType.SHARED,
            fare_amount=event.fare_amount,
            duration_minutes=event.duration_minutes,
            distance_km=event.distance_km,
            shared_ride_attributes=SharedRideAttributes(
                passenger_count=event.passenger_count,
                pooling_score=event.pooling_score,
            ),
        )

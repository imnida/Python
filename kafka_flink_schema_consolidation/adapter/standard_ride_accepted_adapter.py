from ..events.driver_ride_accepted_standard_event import DriverRideAcceptedStandardEvent
from ..model.event_type import EventType
from ..model.ride_type import RideType
from ..schema.driver_ride_activity_record import DriverRideActivityRecord
from ..schema.standard_ride_attributes import StandardRideAttributes


class StandardRideAcceptedAdapter:
    """No framework dependency. Pure transformation logic."""

    def adapt(self, org_id: str, event: DriverRideAcceptedStandardEvent) -> DriverRideActivityRecord:
        return DriverRideActivityRecord(
            event_time=event.event_time,
            driver_id=event.driver_id,
            ride_id=event.ride_id,
            city_id=event.city_id,
            pickup_lat=event.pickup_lat,
            pickup_lng=event.pickup_lng,
            event_type=EventType.ACCEPTED,
            ride_type=RideType.STANDARD,
            estimated_duration_minutes=event.estimated_duration_minutes,
            estimated_fare=event.estimated_fare,
            standard_ride_attributes=StandardRideAttributes(
                vehicle_class=event.vehicle_class,
                surge_multiplier=event.surge_multiplier,
            ),
        )

from __future__ import annotations

from typing import Any, Callable, Dict, NamedTuple, Tuple

from ..model.event_type import EventType
from ..model.ride_type import RideType
from ..schema.driver_ride_activity_record import DriverRideActivityRecord

from .standard_ride_accepted_adapter import StandardRideAcceptedAdapter
from .standard_ride_started_adapter import StandardRideStartedAdapter
from .standard_ride_completed_adapter import StandardRideCompletedAdapter
from .standard_ride_cancelled_adapter import StandardRideCancelledAdapter
from .shared_ride_accepted_adapter import SharedRideAcceptedAdapter
from .shared_ride_started_adapter import SharedRideStartedAdapter
from .shared_ride_completed_adapter import SharedRideCompletedAdapter
from .shared_ride_cancelled_adapter import SharedRideCancelledAdapter
from .scheduled_ride_accepted_adapter import ScheduledRideAcceptedAdapter
from .scheduled_ride_started_adapter import ScheduledRideStartedAdapter
from .scheduled_ride_completed_adapter import ScheduledRideCompletedAdapter
from .scheduled_ride_cancelled_adapter import ScheduledRideCancelledAdapter

# Event-class factory functions (raw dict → typed event)
from ..events.driver_ride_accepted_standard_event import DriverRideAcceptedStandardEvent
from ..events.driver_ride_accepted_shared_event import DriverRideAcceptedSharedEvent
from ..events.driver_ride_accepted_scheduled_event import DriverRideAcceptedScheduledEvent
from ..events.driver_ride_started_standard_event import DriverRideStartedStandardEvent
from ..events.driver_ride_started_shared_event import DriverRideStartedSharedEvent
from ..events.driver_ride_started_scheduled_event import DriverRideStartedScheduledEvent
from ..events.driver_ride_completed_standard_event import DriverRideCompletedStandardEvent
from ..events.driver_ride_completed_shared_event import DriverRideCompletedSharedEvent
from ..events.driver_ride_completed_scheduled_event import DriverRideCompletedScheduledEvent
from ..events.driver_ride_cancelled_standard_event import DriverRideCancelledStandardEvent
from ..events.driver_ride_cancelled_shared_event import DriverRideCancelledSharedEvent
from ..events.driver_ride_cancelled_scheduled_event import DriverRideCancelledScheduledEvent

# A bound adapter is a callable that accepts (org_id, raw_event_dict) and returns a record.
_BoundAdapter = Callable[[str, Dict[str, Any]], DriverRideActivityRecord]
_RegistryKey = Tuple[EventType, RideType]


class AdapterRegistry:
    """Maps (EventType, RideType) discriminator pairs to the appropriate adapter.

    Stores type-erased bound adapters internally.  Adding a new ride variant
    means adding one adapter class and one ``register`` call in
    ``with_all_adapters`` — nothing else changes.
    """

    def __init__(self) -> None:
        self._registry: Dict[_RegistryKey, _BoundAdapter] = {}

    def register(
        self,
        adapter: Any,
        from_map: Callable[[Dict[str, Any]], Any],
        event_type: EventType,
        ride_type: RideType,
    ) -> AdapterRegistry:
        """Bind an adapter for a specific (EventType, RideType) combination.

        Args:
            adapter:    The adapter instance whose ``adapt`` method will be called.
            from_map:   Deserialiser that converts a raw ``dict`` to the typed event.
            event_type: Discriminator for the event lifecycle stage.
            ride_type:  Discriminator for the ride product type.
        """
        def _bound(org_id: str, raw: Dict[str, Any]) -> DriverRideActivityRecord:
            return adapter.adapt(org_id, from_map(raw))

        self._registry[(event_type, ride_type)] = _bound
        return self

    def adapt(
        self,
        org_id: str,
        raw: Dict[str, Any],
        event_type: EventType,
        ride_type: RideType,
    ) -> DriverRideActivityRecord:
        """Look up and execute the adapter for the given discriminators.

        Raises:
            KeyError: if no adapter is registered for the combination.
        """
        key = (event_type, ride_type)
        bound = self._registry.get(key)
        if bound is None:
            raise KeyError(
                f"No adapter registered for EventType={event_type!r}, RideType={ride_type!r}"
            )
        return bound(org_id, raw)

    @classmethod
    def with_all_adapters(cls) -> AdapterRegistry:
        """Factory that returns a registry pre-loaded with all 12 adapters."""
        registry = cls()
        registry.register(StandardRideAcceptedAdapter(),  DriverRideAcceptedStandardEvent.from_map,   EventType.ACCEPTED,   RideType.STANDARD)
        registry.register(StandardRideStartedAdapter(),   DriverRideStartedStandardEvent.from_map,    EventType.STARTED,    RideType.STANDARD)
        registry.register(StandardRideCompletedAdapter(), DriverRideCompletedStandardEvent.from_map,  EventType.COMPLETED,  RideType.STANDARD)
        registry.register(StandardRideCancelledAdapter(), DriverRideCancelledStandardEvent.from_map,  EventType.CANCELLED,  RideType.STANDARD)
        registry.register(SharedRideAcceptedAdapter(),    DriverRideAcceptedSharedEvent.from_map,     EventType.ACCEPTED,   RideType.SHARED)
        registry.register(SharedRideStartedAdapter(),     DriverRideStartedSharedEvent.from_map,      EventType.STARTED,    RideType.SHARED)
        registry.register(SharedRideCompletedAdapter(),   DriverRideCompletedSharedEvent.from_map,    EventType.COMPLETED,  RideType.SHARED)
        registry.register(SharedRideCancelledAdapter(),   DriverRideCancelledSharedEvent.from_map,    EventType.CANCELLED,  RideType.SHARED)
        registry.register(ScheduledRideAcceptedAdapter(), DriverRideAcceptedScheduledEvent.from_map,  EventType.ACCEPTED,   RideType.SCHEDULED)
        registry.register(ScheduledRideStartedAdapter(),  DriverRideStartedScheduledEvent.from_map,   EventType.STARTED,    RideType.SCHEDULED)
        registry.register(ScheduledRideCompletedAdapter(),DriverRideCompletedScheduledEvent.from_map, EventType.COMPLETED,  RideType.SCHEDULED)
        registry.register(ScheduledRideCancelledAdapter(),DriverRideCancelledScheduledEvent.from_map, EventType.CANCELLED,  RideType.SCHEDULED)
        return registry

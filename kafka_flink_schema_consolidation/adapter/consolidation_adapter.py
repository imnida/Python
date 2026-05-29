from __future__ import annotations

import json
from typing import Any, Dict

from ..model.event_type import EventType
from ..model.ride_type import RideType
from ..schema.driver_ride_activity_record import DriverRideActivityRecord
from .adapter_registry import AdapterRegistry


class ConsolidationAdapter:
    """Framework integration layer: parses raw JSON events and routes them.

    Equivalent to Flink's ``MapFunction<String, DriverRideActivityRecord>``.
    All transformation logic lives in the individual RecordAdapter
    implementations, which carry no framework dependency and can be unit
    tested without any infrastructure setup.
    """

    def __init__(self, registry: AdapterRegistry | None = None) -> None:
        self._registry = registry or AdapterRegistry.with_all_adapters()

    def map(self, org_id: str, raw_json: str) -> DriverRideActivityRecord:
        """Parse a raw JSON event string and return a consolidated record.

        Args:
            org_id:   Organisational identifier for multi-tenant pipelines.
            raw_json: UTF-8 JSON string from the Kafka topic.

        Raises:
            ValueError: if the JSON cannot be parsed.
            KeyError:   if the (eventType, rideType) pair has no registered adapter.
        """
        try:
            payload: Dict[str, Any] = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Failed to parse event JSON: {exc}") from exc

        event_type = _parse_event_type(payload.get("eventType", ""))
        ride_type = _parse_ride_type(payload.get("rideType", ""))

        return self._registry.adapt(org_id, payload, event_type, ride_type)


def _parse_event_type(value: str) -> EventType:
    try:
        return EventType(value.upper())
    except ValueError:
        return EventType.ACCEPTED


def _parse_ride_type(value: str) -> RideType:
    try:
        return RideType(value.upper())
    except ValueError:
        return RideType.STANDARD

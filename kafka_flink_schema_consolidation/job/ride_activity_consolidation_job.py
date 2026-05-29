"""Streaming pipeline simulation for the ride-activity consolidation job.

In production this would be backed by a real Kafka consumer and an Iceberg
sink.  This module provides a drop-in simulation that processes a sequence of
JSON event strings and emits consolidated DriverRideActivityRecord instances —
useful for integration testing without infrastructure dependencies.
"""
from __future__ import annotations

import json
import sys
from typing import Iterable, Iterator, List

from ..adapter.consolidation_adapter import ConsolidationAdapter
from ..schema.driver_ride_activity_record import DriverRideActivityRecord


class RideActivityConsolidationJob:
    """Simulated consolidation pipeline.

    Usage::

        job = RideActivityConsolidationJob(org_id="acme")
        records = list(job.process(json_event_strings))

    Exactly-once semantics note: when deployed with a real Kafka source and an
    Iceberg sink, checkpoint intervals keep Kafka offsets in sync with Iceberg
    commits.  This class intentionally omits that concern to stay infrastructure-
    free; inject a real adapter registry to add that layer.
    """

    def __init__(self, org_id: str = "default") -> None:
        self._org_id = org_id
        self._adapter = ConsolidationAdapter()

    def process(self, events: Iterable[str]) -> Iterator[DriverRideActivityRecord]:
        """Yield one consolidated record per input JSON string.

        Malformed JSON is logged to stderr and skipped rather than crashing the
        pipeline — matching Flink's side-output / dead-letter pattern.
        """
        for raw_json in events:
            try:
                yield self._adapter.map(self._org_id, raw_json)
            except (ValueError, KeyError) as exc:
                print(f"[WARN] Skipping event — {exc}", file=sys.stderr)

    @staticmethod
    def sample_events() -> List[str]:
        """Return one sample JSON string for each of the 12 variants."""
        base = {
            "eventTime": 1_700_000_000,
            "driverId": "d-001",
            "rideId": "r-001",
            "cityId": "nyc",
            "pickupLat": 40.7128,
            "pickupLng": -74.0060,
            "estimatedDurationMinutes": 20,
            "estimatedFare": 18.50,
        }

        samples = []

        # Standard rides
        for event_type in ("ACCEPTED", "STARTED"):
            samples.append(json.dumps({**base, "eventType": event_type, "rideType": "STANDARD",
                                        "vehicleClass": "UberX", "surgeMultiplier": 1.2}))
        samples.append(json.dumps({**base, "eventType": "COMPLETED", "rideType": "STANDARD",
                                    "vehicleClass": "UberX", "surgeMultiplier": 1.2,
                                    "fareAmount": 22.10, "durationMinutes": 23, "distanceKm": 8.4}))
        samples.append(json.dumps({**base, "eventType": "CANCELLED", "rideType": "STANDARD",
                                    "vehicleClass": "UberX", "surgeMultiplier": 1.0,
                                    "cancellationReason": "DRIVER_NO_SHOW"}))

        # Shared rides
        for event_type in ("ACCEPTED", "STARTED"):
            samples.append(json.dumps({**base, "eventType": event_type, "rideType": "SHARED",
                                        "passengerCount": 2, "poolingScore": 0.87}))
        samples.append(json.dumps({**base, "eventType": "COMPLETED", "rideType": "SHARED",
                                    "passengerCount": 2, "poolingScore": 0.87,
                                    "fareAmount": 14.00, "durationMinutes": 25, "distanceKm": 9.1}))
        samples.append(json.dumps({**base, "eventType": "CANCELLED", "rideType": "SHARED",
                                    "passengerCount": 1, "poolingScore": 0.50,
                                    "cancellationReason": "PASSENGER_CANCELLED"}))

        # Scheduled rides
        for event_type in ("ACCEPTED", "STARTED"):
            samples.append(json.dumps({**base, "eventType": event_type, "rideType": "SCHEDULED",
                                        "scheduledTime": 1_700_003_600, "advanceBookingMinutes": 60}))
        samples.append(json.dumps({**base, "eventType": "COMPLETED", "rideType": "SCHEDULED",
                                    "scheduledTime": 1_700_003_600, "advanceBookingMinutes": 60,
                                    "fareAmount": 25.00, "durationMinutes": 30, "distanceKm": 11.2}))
        samples.append(json.dumps({**base, "eventType": "CANCELLED", "rideType": "SCHEDULED",
                                    "scheduledTime": 1_700_003_600, "advanceBookingMinutes": 60,
                                    "cancellationReason": "WEATHER"}))

        return samples


def main() -> None:
    """Run the consolidation job against sample events and print the output."""
    job = RideActivityConsolidationJob(org_id="demo-org")
    print(f"Processing {len(RideActivityConsolidationJob.sample_events())} sample events...\n")
    for record in job.process(RideActivityConsolidationJob.sample_events()):
        print(
            f"[{record.event_type.value:9s} | {record.ride_type.value:9s}] "
            f"ride={record.ride_id}  driver={record.driver_id}  "
            f"fare={record.fare_amount}  cancelled={record.cancellation_reason}"
        )


if __name__ == "__main__":
    main()

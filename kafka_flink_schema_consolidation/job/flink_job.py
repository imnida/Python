"""Production Flink job using PyFlink + Kafka source.

Requires:
    pip install apache-flink kafka-python
    A running Kafka broker and Flink cluster.

Run:
    python flink_job.py --brokers localhost:9092 --topic ride-events --org acme
"""
from __future__ import annotations

import argparse
import json
import logging

from pyflink.common import WatermarkStrategy
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import (
    KafkaSource,
    KafkaOffsetResetStrategy,
)

from ..adapter.consolidation_adapter import ConsolidationAdapter

logger = logging.getLogger(__name__)


def build_job(brokers: str, topic: str, org_id: str) -> None:
    env = StreamExecutionEnvironment.get_execution_environment()
    env.enable_checkpointing(30_000)          # 30-second checkpoint interval
    env.get_checkpoint_config().set_min_pause_between_checkpoints(30_000)

    source = (
        KafkaSource.builder()
        .set_bootstrap_servers(brokers)
        .set_topics(topic)
        .set_group_id("ride-consolidation")
        .set_starting_offsets(KafkaOffsetResetStrategy.LATEST)
        .set_value_only_deserializer(SimpleStringSchema())
        .build()
    )

    adapter = ConsolidationAdapter()

    (
        env.from_source(source, WatermarkStrategy.no_watermarks(), "Kafka ride-events")
           .map(lambda raw_json: _safe_adapt(adapter, org_id, raw_json))
           .filter(lambda r: r is not None)
           # Replace .print() with an Iceberg / S3 sink for production
           .print()
    )

    env.execute("RideActivityConsolidationJob")


def _safe_adapt(adapter: ConsolidationAdapter, org_id: str, raw_json: str):
    try:
        return adapter.map(org_id, raw_json)
    except (ValueError, KeyError) as exc:
        logger.warning("Skipping malformed event: %s", exc)
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--brokers", default="localhost:9092")
    parser.add_argument("--topic",   default="ride-events")
    parser.add_argument("--org",     default="default")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    build_job(args.brokers, args.topic, args.org)

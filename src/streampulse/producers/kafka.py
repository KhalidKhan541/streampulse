"""Kafka producer wrapper."""

import json
import logging
from typing import Any

from confluent_kafka import Producer

from streampulse.config import get_settings

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    """Thin wrapper over confluent_kafka Producer with delivery callbacks."""

    def __init__(self, config: dict[str, Any] | None = None):
        settings = get_settings()
        default_config = {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "acks": "all",
            "enable.idempotence": True,
            "compression.type": "lz4",
            "linger.ms": 5,
            "batch.size": 65536,
        }
        if config:
            default_config.update(config)
        self._producer = Producer(default_config)

    def _delivery_callback(self, err, msg):
        if err:
            logger.error("Message delivery failed: %s", err)
        else:
            logger.debug("Delivered to %s [%s]", msg.topic(), msg.partition())

    def send(self, topic: str, key: str, value: dict[str, Any]) -> None:
        self._producer.produce(
            topic=topic,
            key=key.encode("utf-8"),
            value=json.dumps(value, default=str).encode("utf-8"),
            on_delivery=self._delivery_callback,
        )
        self._producer.poll(0)

    def flush(self, timeout: float = 10.0) -> int:
        return self._producer.flush(timeout)

    def close(self) -> None:
        self.flush()

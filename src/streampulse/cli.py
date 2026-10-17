"""StreamPulse CLI entry points."""

import argparse
import asyncio
import logging
import sys
import time
from datetime import datetime, timezone

from streampulse.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def produce(args):
    """Generate synthetic events and send them to Kafka."""
    from streampulse.producers.kafka import KafkaEventProducer
    from streampulse.producers.synthetic import EventProducer

    settings = get_settings()
    synthetic = EventProducer(rate_per_second=args.rate, seed=args.seed)
    kafka = KafkaEventProducer()

    logger.info("Producing %d events at %d/sec to topic=%s",
                args.count, args.rate, settings.kafka_topic_raw_events)

    produced = 0
    interval = 1.0 / args.rate
    for _ in range(args.count):
        event = synthetic.generate_event()
        kafka.send(
            topic=settings.kafka_topic_raw_events,
            key=event.user_id,
            value=event.model_dump(mode="json"),
        )
        produced += 1
        if produced % 1000 == 0:
            kafka.flush()
            logger.info("Produced %d events", produced)
        time.sleep(interval)

    kafka.flush()
    logger.info("Done. Produced %d events total.", produced)
    return 0


def consume(args):
    """Consume, enrich, aggregate, and store events."""
    from streampulse.config import get_settings
    from streampulse.processors.aggregation import TumblingWindowAggregator
    from streampulse.processors.anomaly import ZScoreAnomalyDetector
    from streampulse.processors.enrichment import EventEnricher
    from streampulse.stores.clickhouse import ClickHouseStore

    settings = get_settings()
    enricher = EventEnricher()
    aggregator = TumblingWindowAggregator(window_size_seconds=settings.window_size_seconds)
    detector = ZScoreAnomalyDetector(
        threshold_sigma=settings.anomaly_threshold_sigma,
        window_size=settings.anomaly_window_seconds // settings.window_size_seconds,
    )
    store = ClickHouseStore()

    logger.info(
        "Starting consumer: group=%s topic=%s window=%ds",
        settings.kafka_consumer_group,
        settings.kafka_topic_raw_events,
        settings.window_size_seconds,
    )
    logger.info("Press Ctrl+C to stop.")

    try:
        while True:
            now = datetime.now(timezone.utc)
            closed = aggregator.close_windows(now)
            if closed:
                metrics = aggregator.get_metrics_for_storage(closed)
                metric_dicts = [m.model_dump() for m in metrics]
                store.insert_windowed_metrics(metric_dicts)
                alerts = detector.process_batch(metrics)
                if alerts:
                    store.insert_anomaly_alerts([a.model_dump() for a in alerts])
                    for a in alerts:
                        logger.warning(
                            "ANOMALY: %s=%.2f (expected=%.2f, z=%.2f, severity=%s)",
                            a.metric_name, a.metric_value, a.expected_value,
                            a.sigma_deviation, a.severity,
                        )

            enricher.cleanup_expired(now)
            time.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
        closed = aggregator.close_windows()
        if closed:
            metrics = aggregator.get_metrics_for_storage(closed)
            store.insert_windowed_metrics([m.model_dump() for m in metrics])
        store.close()
        return 0


def serve(args):
    """Start the REST API."""
    import uvicorn
    from streampulse.api.app import create_app

    settings = get_settings()
    app = create_app()
    logger.info("Starting API on %s:%d", settings.api_host, settings.api_port)
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
    return 0


def init_clickhouse():
    """Create ClickHouse tables."""
    from streampulse.stores.clickhouse import ClickHouseStore

    settings = get_settings()
    store = ClickHouseStore()

    ddl_path = "deploy/clickhouse-init.sql"
    try:
        with open(ddl_path) as f:
            statements = f.read().split(";")
        for stmt in statements:
            stmt = stmt.strip()
            if stmt and not stmt.startswith("--"):
                store._client.execute(stmt)
        logger.info("ClickHouse tables initialized.")
    except FileNotFoundError:
        logger.error("DDL file not found: %s", ddl_path)
        return 1
    finally:
        store.close()
    return 0


def main():
    parser = argparse.ArgumentParser(
        prog="streampulse",
        description="StreamPulse — real-time streaming data platform",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_produce = sub.add_parser("produce", help="Generate and send synthetic events")
    p_produce.add_argument("--rate", type=int, default=100, help="Events per second")
    p_produce.add_argument("--count", type=int, default=1000, help="Total events to produce")
    p_produce.add_argument("--seed", type=int, default=None, help="Random seed")

    p_consume = sub.add_parser("consume", help="Start the stream processor")

    p_serve = sub.add_parser("serve", help="Start the REST API")

    p_init = sub.add_parser("init-clickhouse", help="Initialize ClickHouse tables")

    args = parser.parse_args()

    if args.command == "produce":
        return produce(args)
    elif args.command == "consume":
        return consume(args)
    elif args.command == "serve":
        return serve(args)
    elif args.command == "init-clickhouse":
        return init_clickhouse()

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())

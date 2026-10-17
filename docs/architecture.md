"""Architecture overview for StreamPulse."""

# Architecture

StreamPulse is a real-time streaming data engineering platform designed for high-throughput event processing with low latency.

## System Components

### 1. Event Producers
- **Synthetic Producer** — generates realistic clickstream events for testing
- **Kafka Producer** — wraps confluent-kafka with idempotent delivery

### 2. Stream Processors
- **EventEnricher** — adds session context, geo data, and computed features to raw events
- **TumblingWindowAggregator** — aggregates events into fixed-size tumbling windows
- **ZScoreAnomalyDetector** — detects statistical anomalies in windowed metrics

### 3. Storage Layer
- **ClickHouse** — columnar OLAP database for analytics queries on enriched events and metrics
- **PostgreSQL** — metadata and configuration storage
- **Redis** — caching and session state

### 4. API Layer
- **FastAPI** — high-performance REST API for querying metrics, anomalies, and time-series data

## Data Flow

```
1. Events produced to Kafka topic "events.raw"
2. Consumer reads events from Kafka
3. EventEnricher adds session context → "events.enriched"
4. TumblingWindowAggregator computes windowed metrics
5. ZScoreAnomalyDetector scans for anomalies → "events.alerts"
6. ClickHouse stores enriched events + windowed metrics + anomaly alerts
7. FastAPI serves queries from ClickHouse
```

## Window Types

- **Tumbling Windows** — fixed-size, non-overlapping (default: 60 seconds)
- **Session Windows** — gap-based, auto-closed after inactivity

## Anomaly Detection

Z-score based detection:
- Maintains rolling history of windowed metric values
- Computes mean and standard deviation over the history
- Flags values exceeding `threshold_sigma` standard deviations
- Severity levels: WARNING (3σ), CRITICAL (4.5σ)

## Scaling Considerations

- **Kafka Partitions** — scale by increasing partition count
- **Consumer Groups** — multiple processor instances share partitions
- **ClickHouse** — distributed tables for horizontal scaling
- **Stateful Processors** — session state is in-memory; for durability, consider RocksDB or external state store

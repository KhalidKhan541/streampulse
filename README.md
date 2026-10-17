# StreamPulse — Real-Time Streaming Data Platform

[![CI](https://github.com/KhalidKhan541/streampulse/actions/workflows/ci.yml/badge.svg)](https://github.com/KhalidKhan541/streampulse/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> A production-grade real-time streaming data engineering platform for event ingestion, stream processing, anomaly detection, and OLAP analytics.

---

## What Is StreamPulse?

StreamPulse is a real-time data engineering platform built on **Apache Kafka** that:

- **Ingests** high-throughput event streams (clicks, purchases, signups)
- **Enriches** events with session context, geolocation, and computed features
- **Processes** events through windowed aggregations and anomaly detection
- **Stores** enriched data in ClickHouse for sub-second OLAP queries
- **Serves** a REST API for real-time metrics, dashboards, and alerts

This is distinct from batch ELT pipelines (Airflow + dbt). StreamPulse handles **continuous, low-latency event streams**.

---

## Architecture

```
┌──────────────┐     ┌─────────────────────────────────────────┐
│  Event       │     │           Apache Kafka                   │
│  Producers   │────▶│  events.raw  →  events.enriched          │
└──────────────┘     │       │              │                   │
                     │  events.alerts ◀─────┘                   │
                     └──────────┬───────────────────────────────┘
                                │
                     ┌──────────▼───────────────────────────────┐
                     │      StreamPulse Processor                │
                     │  ┌──────────────────────────────────┐    │
                     │  │  Event Enricher                   │    │
                     │  │  Session Builder                  │    │
                     │  │  Windowed Aggregator              │    │
                     │  │  Anomaly Detector (Z-score)       │    │
                     │  └──────────────────────────────────┘    │
                     └──────────┬───────────────────────────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │  ClickHouse   │ │  PostgreSQL  │ │    Redis     │
      │  (OLAP)       │ │  (metadata)  │ │  (cache)     │
      └──────┬───────┘ └──────────────┘ └──────────────┘
             │
      ┌──────▼───────┐
      │  FastAPI     │
      │  REST API    │
      └──────────────┘
```

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/KhalidKhan541/streampulse.git
cd streampulse

# 2. Copy environment
cp .env.example .env

# 3. Start infrastructure
docker compose up -d kafka clickhouse postgres redis

# 4. Install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 5. Initialize ClickHouse tables
python -m streampulse.cli init-clickhouse

# 6. Start the stream processor (in a new terminal)
python -m streampulse.cli consume

# 7. Start generating events (in another terminal)
python -m streampulse.cli produce --rate 100

# 8. Start the API (in another terminal)
python -m streampulse.cli serve
```

Open http://localhost:8000/docs for the interactive API.

---

## Project Structure

```
streampulse/
├── src/streampulse/
│   ├── config/          # Typed settings and env parsing
│   ├── producers/       # Kafka event producers
│   ├── processors/      # Stream enrichment, aggregation, anomaly detection
│   ├── stores/          # ClickHouse, PostgreSQL, Redis clients
│   ├── cli.py           # CLI entry points
│   └── api/             # FastAPI metrics API
├── tests/
│   ├── unit/            # Unit tests for processors
│   └── integration/     # Integration tests with real Kafka
├── deploy/              # Docker Compose, Kubernetes manifests
├── dashboards/          # Grafana dashboards
└── docs/                # Detailed documentation
```

---

## Key Features

| Feature | Description |
|---------|-------------|
| **Event Enrichment** | Geo-IP, user-agent parsing, session joining |
| **Windowed Aggregation** | Tumbling, sliding, and session windows |
| **Anomaly Detection** | Z-score based real-time anomaly detection |
| **Session Builder** | Automatic session construction from event streams |
| **OLAP Storage** | ClickHouse for sub-second analytical queries |
| **REST API** | Real-time metrics, dashboards, alerting |
| **Monitoring** | Health checks, metrics, structured logging |

---

## Development

```bash
# Run tests
pytest tests/ -v --cov=streampulse --cov-report=html

# Lint
ruff check src/ tests/

# Format
black src/ tests/

# Type check
mypy src/
```

---

## Documentation

- [Architecture Deep Dive](docs/architecture.md)
- [API Reference](docs/api.md)
- [Data Pipeline Guide](docs/pipelines.md)
- [Deployment Guide](docs/deployment.md)
- [Operations Runbook](docs/operations.md)

---

## Tech Stack

- **Apache Kafka** — Event streaming backbone
- **ClickHouse** — Columnar OLAP database for analytics
- **PostgreSQL** — Metadata and configuration storage
- **Redis** — Caching and session state
- **FastAPI** — High-performance REST API
- **Python 3.11+** — Async, type-safe, production-grade

---

## License

MIT License — see [LICENSE](LICENSE)

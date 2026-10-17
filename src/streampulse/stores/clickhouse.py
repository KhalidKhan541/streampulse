"""ClickHouse storage client with async insert support."""

import json
import logging
from datetime import datetime
from typing import Any

from clickhouse_driver import Client

from streampulse.config import get_settings

logger = logging.getLogger(__name__)


class ClickHouseStore:
    """Manages writes to and reads from ClickHouse for analytics tables."""

    def __init__(self):
        settings = get_settings()
        self._client = Client(
            host=settings.clickhouse_host,
            port=settings.clickhouse_port,
            user=settings.clickhouse_user,
            password=settings.clickhouse_password,
            database=settings.clickhouse_database,
        )

    def insert_enriched_events(self, events: list[dict[str, Any]]) -> int:
        if not events:
            return 0
        rows = [
            (
                e.get("event_id", ""),
                e.get("event_type", ""),
                e.get("event_time"),
                e.get("user_id", ""),
                e.get("session_id", ""),
                e.get("page_url", ""),
                e.get("referrer", ""),
                e.get("device_type", ""),
                e.get("browser", ""),
                e.get("os", ""),
                e.get("country", ""),
                e.get("city", ""),
                e.get("ip_hash", ""),
                e.get("amount", 0.0),
                e.get("currency", "USD"),
                json.dumps(e.get("properties", {})),
                e.get("session_duration", 0),
                e.get("page_sequence", 0),
                1 if e.get("is_returning") else 0,
                e.get("time_on_page_ms", 0),
                e.get("ingested_at"),
                e.get("processed_at", datetime.utcnow()),
            )
            for e in events
        ]
        self._client.execute(
            """INSERT INTO enriched_events (
                event_id, event_type, event_time, user_id, session_id,
                page_url, referrer, device_type, browser, os,
                country, city, ip_hash, amount, currency, properties,
                session_duration, page_sequence, is_returning, time_on_page_ms,
                ingested_at, processed_at
            ) VALUES""",
            rows,
        )
        logger.info("Inserted %d enriched events", len(rows))
        return len(rows)

    def insert_windowed_metrics(self, metrics: list[dict[str, Any]]) -> int:
        if not metrics:
            return 0
        rows = [
            (
                m.get("window_start"),
                m.get("window_type", "tumbling"),
                m.get("event_type", "all"),
                m.get("metric_name", ""),
                m.get("metric_value", 0.0),
                m.get("event_count", 0),
                m.get("unique_users", 0),
                m.get("computed_at", datetime.utcnow()),
            )
            for m in metrics
        ]
        self._client.execute(
            """INSERT INTO windowed_metrics (
                window_start, window_type, event_type, metric_name,
                metric_value, event_count, unique_users, computed_at
            ) VALUES""",
            rows,
        )
        return len(rows)

    def insert_anomaly_alerts(self, alerts: list[dict[str, Any]]) -> int:
        if not alerts:
            return 0
        rows = [
            (
                a.get("alert_id", ""),
                a.get("detected_at"),
                a.get("metric_name", ""),
                a.get("metric_value", 0.0),
                a.get("expected_value", 0.0),
                a.get("sigma_deviation", 0.0),
                a.get("window_seconds", 0),
                a.get("severity", "info"),
                1 if a.get("resolved") else 0,
                a.get("resolved_at") or datetime(1970, 1, 1),
            )
            for a in alerts
        ]
        self._client.execute(
            """INSERT INTO anomaly_alerts (
                alert_id, detected_at, metric_name, metric_value,
                expected_value, sigma_deviation, window_seconds,
                severity, resolved, resolved_at
            ) VALUES""",
            rows,
        )
        return len(rows)

    def query(self, sql: str, params: dict | None = None) -> list:
        return self._client.execute(sql, params or {})

    def close(self) -> None:
        self._client.disconnect()

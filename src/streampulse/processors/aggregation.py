"""Windowed aggregation: tumbling windows with event counts, unique users, and metrics."""

from collections import defaultdict
from datetime import datetime, timezone

from streampulse.models import EnrichedEvent, WindowedMetric


class TumblingWindowAggregator:
    """Aggregates enriched events into fixed-size tumbling windows."""

    def __init__(self, window_size_seconds: int = 60):
        self.window_size = window_size_seconds
        self._windows: dict[int, dict] = {}
        self._closed_windows: list[dict] = []

    def _window_key(self, event_time: datetime) -> int:
        epoch = int(event_time.timestamp())
        return epoch - (epoch % self.window_size)

    def add_event(self, event: EnrichedEvent) -> None:
        key = self._window_key(event.event_time)
        if key not in self._windows:
            self._windows[key] = {
                "window_start": datetime.fromtimestamp(key, tz=timezone.utc),
                "events": 0,
                "unique_users": set(),
                "revenue": 0.0,
                "event_types": defaultdict(lambda: {"count": 0, "users": set()}),
                "pages": defaultdict(int),
                "devices": defaultdict(int),
                "countries": defaultdict(int),
                "is_returning_count": 0,
                "total_session_duration": 0,
            }

        w = self._windows[key]
        w["events"] += 1
        w["unique_users"].add(event.user_id)
        w["revenue"] += event.amount
        w["event_types"][event.event_type.value]["count"] += 1
        w["event_types"][event.event_type.value]["users"].add(event.user_id)
        w["pages"][event.page_url] += 1
        w["devices"][event.device_type.value] += 1
        w["countries"][event.country] += 1
        if event.is_returning:
            w["is_returning_count"] += 1
        w["total_session_duration"] += event.session_duration

    def close_windows(self, current_time: datetime | None = None) -> list[dict]:
        """Close all windows that have elapsed and return them."""
        current_time = current_time or datetime.now(timezone.utc)
        current_key = self._window_key(current_time)

        to_close = [k for k in self._windows if k < current_key]
        results = []

        for key in sorted(to_close):
            w = self._windows.pop(key)
            result = {
                "window_start": w["window_start"],
                "window_type": "tumbling",
                "event_count": w["events"],
                "unique_users": len(w["unique_users"]),
                "revenue": round(w["revenue"], 2),
                "event_type_breakdown": {
                    et: {"count": d["count"], "unique_users": len(d["users"])}
                    for et, d in w["event_types"].items()
                },
                "top_pages": dict(sorted(w["pages"].items(), key=lambda x: -x[1])[:10]),
                "device_breakdown": dict(w["devices"]),
                "country_breakdown": dict(w["countries"]),
                "returning_user_ratio": round(
                    w["is_returning_count"] / max(w["events"], 1), 4
                ),
                "avg_session_duration_sec": round(
                    w["total_session_duration"] / max(w["events"], 1), 2
                ),
            }
            results.append(result)
            self._closed_windows.append(result)

        return results

    def get_metrics_for_storage(self, closed: list[dict]) -> list[WindowedMetric]:
        """Convert closed windows into flat WindowedMetric rows."""
        metrics = []
        for w in closed:
            metrics.append(WindowedMetric(
                window_start=w["window_start"],
                window_type="tumbling",
                event_type="all",
                metric_name="total_events",
                metric_value=w["event_count"],
                event_count=w["event_count"],
                unique_users=w["unique_users"],
            ))
            metrics.append(WindowedMetric(
                window_start=w["window_start"],
                window_type="tumbling",
                event_type="all",
                metric_name="total_revenue",
                metric_value=w["revenue"],
                event_count=w["event_count"],
                unique_users=w["unique_users"],
            ))
            metrics.append(WindowedMetric(
                window_start=w["window_start"],
                window_type="tumbling",
                event_type="all",
                metric_name="returning_user_ratio",
                metric_value=w["returning_user_ratio"],
                event_count=w["event_count"],
                unique_users=w["unique_users"],
            ))
            for et, data in w["event_type_breakdown"].items():
                metrics.append(WindowedMetric(
                    window_start=w["window_start"],
                    window_type="tumbling",
                    event_type=et,
                    metric_name="event_count",
                    metric_value=data["count"],
                    event_count=data["count"],
                    unique_users=data["unique_users"],
                ))
        return metrics

    @property
    def open_windows(self) -> int:
        return len(self._windows)

    @property
    def closed_windows_total(self) -> int:
        return len(self._closed_windows)

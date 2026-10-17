"""Z-score based anomaly detection over windowed metrics."""

import math
from collections import defaultdict, deque
from datetime import datetime, timezone

from streampulse.models import AnomalyAlert, Severity, WindowedMetric


class ZScoreAnomalyDetector:
    """Detects anomalies in streaming metrics using a rolling Z-score approach.

    Maintains a rolling window of values per metric. When a new value arrives
    that is more than `threshold_sigma` standard deviations from the mean of
    the historical window, an anomaly alert is emitted.
    """

    def __init__(
        self,
        threshold_sigma: float = 3.0,
        window_size: int = 120,
        min_samples: int = 20,
    ):
        self.threshold_sigma = threshold_sigma
        self.window_size = window_size
        self.min_samples = min_samples
        self._history: dict[str, deque[float]] = defaultdict(
            lambda: deque(maxlen=window_size)
        )
        self._alerts: list[AnomalyAlert] = []

    def process_metric(self, metric: WindowedMetric) -> AnomalyAlert | None:
        key = f"{metric.metric_name}:{metric.event_type}"
        history = self._history[key]

        alert = None

        if len(history) >= self.min_samples:
            mean = sum(history) / len(history)
            variance = sum((x - mean) ** 2 for x in history) / len(history)
            std_dev = math.sqrt(variance)

            if std_dev > 0:
                z_score = (metric.metric_value - mean) / std_dev

                if abs(z_score) >= self.threshold_sigma:
                    severity = Severity.CRITICAL if abs(z_score) >= self.threshold_sigma * 1.5 else Severity.WARNING
                    alert = AnomalyAlert(
                        metric_name=metric.metric_name,
                        metric_value=metric.metric_value,
                        expected_value=round(mean, 4),
                        sigma_deviation=round(z_score, 4),
                        window_seconds=self.window_size * 60,
                        severity=severity,
                    )
                    self._alerts.append(alert)

        history.append(metric.metric_value)
        return alert

    def process_batch(self, metrics: list[WindowedMetric]) -> list[AnomalyAlert]:
        alerts = []
        for metric in metrics:
            alert = self.process_metric(metric)
            if alert:
                alerts.append(alert)
        return alerts

    @property
    def pending_alerts(self) -> list[AnomalyAlert]:
        return [a for a in self._alerts if not a.resolved]

    def get_metric_stats(self, metric_name: str, event_type: str = "all") -> dict:
        key = f"{metric_name}:{event_type}"
        history = self._history[key]
        if not history:
            return {"count": 0, "mean": 0, "std_dev": 0, "min": 0, "max": 0}
        values = list(history)
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return {
            "count": len(values),
            "mean": round(mean, 4),
            "std_dev": round(math.sqrt(variance), 4),
            "min": round(min(values), 4),
            "max": round(max(values), 4),
        }

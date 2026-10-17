from streampulse.models import WindowedMetric
from streampulse.processors.anomaly import ZScoreAnomalyDetector


def _metric(value, name="total_events"):
    return WindowedMetric(
        window_start=None,
        window_type="tumbling",
        event_type="all",
        metric_name=name,
        metric_value=value,
        event_count=int(value),
        unique_users=1,
    )


def test_no_alert_when_insufficient_samples():
    detector = ZScoreAnomalyDetector(threshold_sigma=3.0, min_samples=5)
    for _ in range(4):
        alert = detector.process_metric(_metric(100.0))
    assert alert is None


def test_no_alert_for_normal_values():
    detector = ZScoreAnomalyDetector(threshold_sigma=3.0, min_samples=20)
    alerts = []
    for _ in range(20):
        alerts.append(detector.process_metric(_metric(100.0)))
    assert all(a is None for a in alerts)


def test_detect_spike():
    detector = ZScoreAnomalyDetector(threshold_sigma=3.0, min_samples=20)
    for _ in range(20):
        detector.process_metric(_metric(100.0))

    alert = detector.process_metric(_metric(500.0))
    assert alert is not None
    assert alert.metric_name == "total_events"
    assert alert.metric_value == 500.0
    assert alert.sigma_deviation > 3.0


def test_detect_drop():
    detector = ZScoreAnomalyDetector(threshold_sigma=3.0, min_samples=20)
    for _ in range(20):
        detector.process_metric(_metric(100.0))

    alert = detector.process_metric(_metric(10.0))
    assert alert is not None
    assert alert.sigma_deviation < -3.0


def test_critical_severity():
    detector = ZScoreAnomalyDetector(threshold_sigma=3.0, min_samples=20)
    for _ in range(20):
        detector.process_metric(_metric(100.0))

    alert = detector.process_metric(_metric(1000.0))
    assert alert is not None
    assert alert.severity == "critical"


def test_get_metric_stats():
    detector = ZScoreAnomalyDetector(threshold_sigma=3.0, min_samples=5)
    for v in [10, 20, 30, 40, 50]:
        detector.process_metric(_metric(float(v)))

    stats = detector.get_metric_stats("total_events")
    assert stats["count"] == 5
    assert stats["mean"] == 30.0


def test_pending_alerts():
    detector = ZScoreAnomalyDetector(threshold_sigma=3.0, min_samples=5)
    for _ in range(10):
        detector.process_metric(_metric(100.0))

    detector.process_metric(_metric(1000.0))
    assert len(detector.pending_alerts) >= 1

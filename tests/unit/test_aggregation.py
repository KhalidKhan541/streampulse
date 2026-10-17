from datetime import datetime, timedelta, timezone

from streampulse.models import DeviceType, EnrichedEvent, EventType
from streampulse.processors.aggregation import TumblingWindowAggregator


def _make_enriched(ts, user_id="u1", event_type=EventType.PAGE_VIEW, amount=0.0):
    return EnrichedEvent(
        event_type=event_type,
        event_time=ts,
        user_id=user_id,
        session_id=f"s-{user_id}",
        page_url="/",
        device_type=DeviceType.DESKTOP,
        country="US",
        amount=amount,
    )


def test_window_basic_aggregation():
    agg = TumblingWindowAggregator(window_size_seconds=60)
    t = datetime(2026, 1, 15, 12, 0, 10, tzinfo=timezone.utc)

    for i in range(5):
        agg.add_event(_make_enriched(t, user_id=f"u{i}"))

    later = t + timedelta(seconds=120)
    closed = agg.close_windows(later)

    assert len(closed) >= 1
    w = closed[0]
    assert w["event_count"] == 5
    assert w["unique_users"] == 5


def test_window_revenue_tracking():
    agg = TumblingWindowAggregator(window_size_seconds=60)
    t = datetime(2026, 1, 15, 12, 0, 10, tzinfo=timezone.utc)

    agg.add_event(_make_enriched(t, event_type=EventType.PURCHASE, amount=49.99))
    agg.add_event(_make_enriched(t, event_type=EventType.PURCHASE, amount=99.99))

    closed = agg.close_windows(t + timedelta(seconds=120))
    assert closed[0]["revenue"] == 149.98


def test_window_deduplication():
    agg = TumblingWindowAggregator(window_size_seconds=60)
    t = datetime(2026, 1, 15, 12, 0, 10, tzinfo=timezone.utc)

    for _ in range(10):
        agg.add_event(_make_enriched(t, user_id="same-user"))

    closed = agg.close_windows(t + timedelta(seconds=120))
    assert closed[0]["unique_users"] == 1
    assert closed[0]["event_count"] == 10


def test_metrics_conversion():
    agg = TumblingWindowAggregator(window_size_seconds=60)
    t = datetime(2026, 1, 15, 12, 0, 10, tzinfo=timezone.utc)

    agg.add_event(_make_enriched(t, event_type=EventType.PAGE_VIEW))

    closed = agg.close_windows(t + timedelta(seconds=120))
    metrics = agg.get_metrics_for_storage(closed)

    assert len(metrics) >= 3
    metric_names = {m.metric_name for m in metrics}
    assert "total_events" in metric_names
    assert "total_revenue" in metric_names


def test_open_and_closed_counts():
    agg = TumblingWindowAggregator(window_size_seconds=60)
    t = datetime(2026, 1, 15, 12, 0, 10, tzinfo=timezone.utc)

    agg.add_event(_make_enriched(t))
    assert agg.open_windows == 1

    closed = agg.close_windows(t + timedelta(seconds=120))
    assert len(closed) == 1
    assert agg.open_windows == 0
    assert agg.closed_windows_total == 1

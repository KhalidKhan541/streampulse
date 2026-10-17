from datetime import datetime, timedelta, timezone

from streampulse.models import DeviceType, EnrichedEvent, EventType
from streampulse.processors.enrichment import EventEnricher
from streampulse.models import RawEvent


def _make_event(user_id="u1", session_id="s1", page="/", event_type=EventType.PAGE_VIEW,
                event_time=None, amount=0.0):
    return RawEvent(
        event_type=event_type,
        event_time=event_time or datetime.now(timezone.utc),
        user_id=user_id,
        session_id=session_id,
        page_url=page,
        device_type=DeviceType.DESKTOP,
        country="US",
        amount=amount,
    )


def test_enrichment_basic():
    enricher = EventEnricher()
    event = _make_event()
    enriched = enricher.enrich(event)

    assert enriched.session_duration == 0
    assert enriched.page_sequence == 1
    assert enriched.is_returning is False


def test_enrichment_returning_user():
    enricher = EventEnricher()
    first = enricher.enrich(_make_event(user_id="u1", session_id="s1"))
    second = enricher.enrich(_make_event(user_id="u1", session_id="s1"))

    assert first.is_returning is False
    assert second.is_returning is True


def test_enrichment_session_duration():
    enricher = EventEnricher()
    t0 = datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    t1 = t0 + timedelta(seconds=45)

    enricher.enrich(_make_event(event_time=t0))
    enriched = enricher.enrich(_make_event(event_time=t1))

    assert enriched.session_duration == 45


def test_enrichment_revenue_accumulation():
    enricher = EventEnricher()
    enricher.enrich(_make_event(event_type=EventType.ADD_TO_CART, amount=0.0))
    enricher.enrich(_make_event(event_type=EventType.PURCHASE, amount=99.99))

    metrics = enricher.get_session_metrics("s1")
    assert metrics is not None
    assert metrics["total_revenue"] == 99.99


def test_cleanup_expired_sessions():
    enricher = EventEnricher(session_timeout_seconds=60)
    old_time = datetime.now(timezone.utc) - timedelta(hours=2)
    enricher.enrich(_make_event(event_time=old_time))

    assert enricher.active_sessions == 1
    cleaned = enricher.cleanup_expired()
    assert cleaned == 1
    assert enricher.active_sessions == 0


def test_multiple_sessions():
    enricher = EventEnricher()
    enricher.enrich(_make_event(session_id="s1"))
    enricher.enrich(_make_event(session_id="s2"))
    assert enricher.active_sessions == 2

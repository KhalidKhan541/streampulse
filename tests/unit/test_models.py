from datetime import datetime, timezone

from streampulse.models import DeviceType, EventType, RawEvent


def test_raw_event_defaults():
    event = RawEvent(
        event_type=EventType.PAGE_VIEW,
        user_id="u1",
        session_id="s1",
        page_url="/",
    )
    assert event.event_id is not None
    assert event.event_time.tzinfo is not None
    assert event.amount == 0.0
    assert event.currency == "USD"


def test_raw_event_utc_enforcement():
    naive = RawEvent(
        event_type=EventType.CLICK,
        event_time=datetime(2026, 1, 15, 10, 0, 0),
        user_id="u1",
        session_id="s1",
        page_url="/",
    )
    assert naive.event_time.tzinfo is not None
    assert naive.event_time.utcoffset().total_seconds() == 0


def test_event_types():
    assert EventType.PAGE_VIEW.value == "page_view"
    assert EventType.PURCHASE.value == "purchase"
    assert len(EventType) >= 8


def test_purchase_event():
    event = RawEvent(
        event_type=EventType.PURCHASE,
        user_id="u1",
        session_id="s1",
        page_url="/checkout",
        amount=49.99,
        currency="EUR",
    )
    assert event.amount == 49.99
    assert event.currency == "EUR"


def test_serialization_round_trip():
    event = RawEvent(
        event_type=EventType.SEARCH,
        user_id="u1",
        session_id="s1",
        page_url="/search",
        properties={"query": "laptop"},
    )
    data = event.model_dump(mode="json")
    restored = RawEvent(**data)
    assert restored.event_id == event.event_id
    assert restored.properties == {"query": "laptop"}

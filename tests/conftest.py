from datetime import datetime, timezone

import pytest

from streampulse.models import DeviceType, EnrichedEvent, EventType, RawEvent


@pytest.fixture
def raw_event() -> RawEvent:
    return RawEvent(
        event_type=EventType.PAGE_VIEW,
        event_time=datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        user_id="user-001",
        session_id="sess-001",
        page_url="/products",
        referrer="https://google.com",
        device_type=DeviceType.MOBILE,
        browser="Chrome",
        os="Android",
        country="US",
        ip_hash="abc123",
        amount=0.0,
        currency="USD",
        properties={"experiment_group": "control"},
    )


@pytest.fixture
def purchase_event() -> RawEvent:
    return RawEvent(
        event_type=EventType.PURCHASE,
        event_time=datetime(2026, 1, 15, 12, 5, 0, tzinfo=timezone.utc),
        user_id="user-001",
        session_id="sess-001",
        page_url="/checkout",
        referrer="https://google.com",
        device_type=DeviceType.MOBILE,
        browser="Chrome",
        os="Android",
        country="US",
        ip_hash="abc123",
        amount=99.99,
        currency="USD",
    )


@pytest.fixture
def enriched_event() -> EnrichedEvent:
    return EnrichedEvent(
        event_type=EventType.PAGE_VIEW,
        event_time=datetime(2026, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        user_id="user-001",
        session_id="sess-001",
        page_url="/products",
        device_type=DeviceType.DESKTOP,
        country="US",
        amount=0.0,
        session_duration=30,
        page_sequence=1,
        is_returning=False,
    )

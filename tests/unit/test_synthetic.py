from streampulse.producers.synthetic import EventProducer
from streampulse.models import EventType


def test_producer_generates_events():
    producer = EventProducer(rate_per_second=100, seed=42)
    event = producer.generate_event()
    assert event.user_id is not None
    assert event.session_id is not None
    assert event.event_type in EventType


def test_producer_deterministic_with_seed():
    p1 = EventProducer(seed=42)
    p2 = EventProducer(seed=42)
    e1 = p1.generate_event()
    e2 = p2.generate_event()
    assert e1.user_id == e2.user_id
    assert e1.event_type == e2.event_type


def test_producer_power_users():
    producer = EventProducer(seed=42)
    user_ids = {producer.generate_event().user_id for _ in range(1000)}
    assert any(uid.startswith("power-user") for uid in user_ids)


def test_producer_purchase_amounts():
    producer = EventProducer(seed=42)
    purchases = [
        producer.generate_event()
        for _ in range(2000)
        if producer.generate_event().event_type == EventType.PURCHASE
    ]
    assert all(p.amount > 0 for p in purchases[:50])


def test_producer_event_types():
    producer = EventProducer(seed=42)
    types = {producer.generate_event().event_type for _ in range(1000)}
    assert len(types) >= 5

"""Event producer for generating realistic synthetic event streams."""

import asyncio
import hashlib
import random
import time
from datetime import datetime, timezone

from streampulse.models import DeviceType, EventType, RawEvent

PAGES = [
    "/", "/products", "/products/1", "/products/2", "/products/3",
    "/cart", "/checkout", "/about", "/blog", "/blog/post-1",
    "/search", "/account", "/account/settings", "/help", "/pricing",
]

REFERRERS = [
    "", "", "", "",  # 80% direct
    "https://google.com", "https://twitter.com", "https://reddit.com",
    "https://facebook.com", "https://linkedin.com",
]

COUNTRIES = ["US", "GB", "DE", "FR", "IN", "JP", "BR", "AU", "CA", "NL"]
BROWSERS = ["Chrome", "Firefox", "Safari", "Edge", "Opera"]
OPERATING_SYSTEMS = ["Windows", "macOS", "Linux", "Android", "iOS"]
CURRENCIES = {"US": "USD", "GB": "GBP", "DE": "EUR", "FR": "EUR", "IN": "INR",
              "JP": "JPY", "BR": "BRL", "AU": "AUD", "CA": "CAD", "NL": "EUR"}

PURCHASE_AMOUNTS = [9.99, 14.99, 24.99, 34.99, 49.99, 79.99, 99.99, 149.99, 199.99, 299.99]

EVENT_TYPE_WEIGHTS = {
    EventType.PAGE_VIEW: 50,
    EventType.CLICK: 25,
    EventType.SCROLL: 12,
    EventType.SEARCH: 5,
    EventType.ADD_TO_CART: 4,
    EventType.PURCHASE: 1.5,
    EventType.SIGNUP: 0.5,
    EventType.LOGIN: 0.8,
    EventType.LOGOUT: 0.3,
    EventType.REMOVE_FROM_CART: 0.7,
    EventType.SHARE: 0.2,
}


def _weighted_choice(choices: dict) -> EventType:
    items = list(choices.keys())
    weights = list(choices.values())
    return random.choices(items, weights=weights, k=1)[0]


class EventProducer:
    """Generates synthetic clickstream events at a given rate."""

    def __init__(self, rate_per_second: int = 100, seed: int | None = None):
        self.rate = rate_per_second
        if seed is not None:
            random.seed(seed)
        self._user_counter = 0
        self._session_map: dict[str, str] = {}

    def _get_user_id(self) -> str:
        """Zipf-like distribution: a few heavy users, many light users."""
        if random.random() < 0.05:
            return f"power-user-{random.randint(1, 50):04d}"
        self._user_counter += 1
        return f"user-{self._user_counter % 50000:05d}"

    def _get_session_id(self, user_id: str) -> str:
        if user_id not in self._session_map or random.random() < 0.02:
            self._session_map[user_id] = str(uuid_hex())
        return self._session_map[user_id]

    def generate_event(self) -> RawEvent:
        event_type = _weighted_choice(EVENT_TYPE_WEIGHTS)
        user_id = self._get_user_id()
        session_id = self._get_session_id(user_id)
        country = random.choice(COUNTRIES)

        amount = 0.0
        currency = "USD"
        if event_type == EventType.PURCHASE:
            amount = random.choice(PURCHASE_AMOUNTS)
            currency = CURRENCIES.get(country, "USD")

        page = random.choice(PAGES)
        if event_type in (EventType.ADD_TO_CART, EventType.REMOVE_FROM_CART):
            page = random.choice(["/products/1", "/products/2", "/products/3"])
        elif event_type == EventType.PURCHASE:
            page = "/checkout"
        elif event_type == EventType.SEARCH:
            page = "/search"

        return RawEvent(
            event_type=event_type,
            event_time=datetime.now(timezone.utc),
            user_id=user_id,
            session_id=session_id,
            page_url=page,
            referrer=random.choice(REFERRERS),
            device_type=DeviceType(random.choices(
                [DeviceType.DESKTOP, DeviceType.MOBILE, DeviceType.TABLET, DeviceType.BOT],
                weights=[45, 40, 10, 5], k=1)[0]),
            browser=random.choice(BROWSERS),
            os=random.choice(OPERATING_SYSTEMS),
            country=country,
            city="",
            ip_hash=hashlib.sha256(f"{user_id}-{random.random()}".encode()).hexdigest()[:16],
            amount=round(amount, 2),
            currency=currency,
            properties={
                "experiment_group": random.choice(["control", "variant_a", "variant_b"]),
                "load_time_ms": random.randint(50, 2000),
            },
        )

    async def produce_async(self, duration_seconds: float = 60.0) -> None:
        """Async generator yielding events at the configured rate."""
        interval = 1.0 / self.rate
        end_time = time.monotonic() + duration_seconds

        while time.monotonic() < end_time:
            event = self.generate_event()
            yield event
            await asyncio.sleep(interval)


def uuid_hex() -> str:
    import uuid as _uuid
    return _uuid.uuid4().hex

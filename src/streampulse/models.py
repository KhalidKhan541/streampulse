import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class EventType(str, Enum):
    PAGE_VIEW = "page_view"
    CLICK = "click"
    SCROLL = "scroll"
    PURCHASE = "purchase"
    SIGNUP = "signup"
    LOGIN = "login"
    LOGOUT = "logout"
    ADD_TO_CART = "add_to_cart"
    REMOVE_FROM_CART = "remove_from_cart"
    SEARCH = "search"
    SHARE = "share"


class DeviceType(str, Enum):
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    BOT = "bot"


class Severity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class RawEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    event_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: str
    session_id: str
    page_url: str
    referrer: str = ""
    device_type: DeviceType = DeviceType.DESKTOP
    browser: str = ""
    os: str = ""
    country: str = ""
    city: str = ""
    ip_hash: str = ""
    amount: float = 0.0
    currency: str = "USD"
    properties: dict[str, Any] = Field(default_factory=dict)

    @field_validator("event_time")
    @classmethod
    def ensure_utc(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)


class EnrichedEvent(RawEvent):
    session_duration: int = 0
    page_sequence: int = 0
    is_returning: bool = False
    time_on_page_ms: int = 0
    processed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WindowedMetric(BaseModel):
    window_start: datetime
    window_type: str
    event_type: str
    metric_name: str
    metric_value: float
    event_count: int
    unique_users: int
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SessionMetrics(BaseModel):
    session_id: str
    user_id: str
    start_time: datetime
    end_time: datetime
    duration_sec: int
    page_count: int
    event_count: int
    total_revenue: float
    device_type: str
    country: str
    top_page: str
    referrer: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AnomalyAlert(BaseModel):
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metric_name: str
    metric_value: float
    expected_value: float
    sigma_deviation: float
    window_seconds: int
    severity: Severity
    resolved: bool = False
    resolved_at: datetime | None = None


class AuditLogEntry(BaseModel):
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    component: str
    action: str
    status: str
    details: str = ""
    duration_ms: int = 0

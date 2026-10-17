"""Stream enrichment: adds session context, geo data, and computed features."""

import time
from datetime import datetime, timezone

from streampulse.models import EnrichedEvent, RawEvent


class SessionState:
    """Tracks per-session state for enrichment."""

    __slots__ = ("start_time", "last_event_time", "page_count", "event_count",
                 "total_revenue", "top_page", "page_visits")

    def __init__(self, start_time: datetime):
        self.start_time = start_time
        self.last_event_time = start_time
        self.page_count: int = 0
        self.event_count: int = 0
        self.total_revenue: float = 0.0
        self.top_page: str = ""
        self.page_visits: dict[str, int] = {}


class EventEnricher:
    """Enriches raw events with session-level context and computed features."""

    def __init__(self, session_timeout_seconds: int = 1800):
        self._sessions: dict[str, SessionState] = {}
        self._known_users: set[str] = set()
        self._session_timeout = session_timeout_seconds

    def _get_or_create_session(self, session_id: str, event_time: datetime) -> SessionState:
        state = self._sessions.get(session_id)
        if state is None:
            state = SessionState(start_time=event_time)
            self._sessions[session_id] = state
        return state

    def enrich(self, event: RawEvent) -> EnrichedEvent:
        session = self._get_or_create_session(event.session_id, event.event_time)

        session_duration = int((event.event_time - session.start_time).total_seconds())
        time_on_page_ms = int((event.event_time - session.last_event_time).total_seconds() * 1000)

        session.event_count += 1
        session.last_event_time = event.event_time
        session.total_revenue += event.amount

        if event.page_url:
            session.page_visits[event.page_url] = session.page_visits.get(event.page_url, 0) + 1
            session.page_count += 1
            session.top_page = max(session.page_visits, key=session.page_visits.get)

        is_returning = event.user_id in self._known_users
        self._known_users.add(event.user_id)

        return EnrichedEvent(
            **event.model_dump(),
            session_duration=session_duration,
            page_sequence=session.event_count,
            is_returning=is_returning,
            time_on_page_ms=max(time_on_page_ms, 0),
        )

    def get_session_metrics(self, session_id: str) -> dict | None:
        state = self._sessions.get(session_id)
        if state is None:
            return None
        return {
            "session_id": session_id,
            "start_time": state.start_time,
            "end_time": state.last_event_time,
            "duration_sec": int((state.last_event_time - state.start_time).total_seconds()),
            "page_count": state.page_count,
            "event_count": state.event_count,
            "total_revenue": state.total_revenue,
            "top_page": state.top_page,
        }

    def cleanup_expired(self, now: datetime | None = None) -> int:
        now = now or datetime.now(timezone.utc)
        expired = [
            sid for sid, state in self._sessions.items()
            if (now - state.last_event_time).total_seconds() > self._session_timeout
        ]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)

    @property
    def active_sessions(self) -> int:
        return len(self._sessions)

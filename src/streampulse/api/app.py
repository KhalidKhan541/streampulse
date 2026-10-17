"""FastAPI application for the StreamPulse metrics API."""

import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from streampulse.config import get_settings

logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime
    uptime_seconds: float


class WindowedMetricResponse(BaseModel):
    window_start: datetime
    window_type: str
    event_type: str
    metric_name: str
    metric_value: float
    event_count: int
    unique_users: int


class AnomalyAlertResponse(BaseModel):
    alert_id: str
    detected_at: datetime
    metric_name: str
    metric_value: float
    expected_value: float
    sigma_deviation: float
    severity: str


class TimeseriesPoint(BaseModel):
    timestamp: datetime
    value: float
    label: str = ""


class MetricsSummary(BaseModel):
    total_events: int
    total_revenue: float
    active_sessions: int
    avg_session_duration: float
    returning_user_ratio: float
    top_pages: list[dict]
    device_breakdown: dict
    country_breakdown: dict
    anomaly_count_24h: int


def create_app() -> FastAPI:
    settings = get_settings()
    import time
    start_time = time.monotonic()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        logger.info("StreamPulse API starting up")
        yield
        logger.info("StreamPulse API shutting down")

    app = FastAPI(
        title="StreamPulse API",
        description="Real-time streaming data metrics API",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.api_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", response_model=HealthResponse)
    async def health():
        return HealthResponse(
            status="healthy",
            service="streampulse-api",
            timestamp=datetime.utcnow(),
            uptime_seconds=round(time.monotonic() - start_time, 2),
        )

    @app.get("/api/v1/metrics/summary", response_model=MetricsSummary)
    async def metrics_summary(
        minutes: int = Query(default=60, ge=1, le=1440),
    ):
        return MetricsSummary(
            total_events=0,
            total_revenue=0.0,
            active_sessions=0,
            avg_session_duration=0.0,
            returning_user_ratio=0.0,
            top_pages=[],
            device_breakdown={},
            country_breakdown={},
            anomaly_count_24h=0,
        )

    @app.get("/api/v1/metrics/timeseries", response_model=list[TimeseriesPoint])
    async def metrics_timeseries(
        metric: str = Query(default="total_events"),
        window_minutes: int = Query(default=5, ge=1, le=1440),
        limit: int = Query(default=120, ge=1, le=1000),
    ):
        return []

    @app.get("/api/v1/anomalies", response_model=list[AnomalyAlertResponse])
    async def anomalies(
        limit: int = Query(default=50, ge=1, le=500),
        severity: str | None = Query(default=None),
    ):
        return []

    @app.get("/api/v1/windows/closed", response_model=list[WindowedMetricResponse])
    async def closed_windows(
        limit: int = Query(default=20, ge=1, le=200),
    ):
        return []

    return app

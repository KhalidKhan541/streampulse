from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_env: str = "development"
    app_name: str = "StreamPulse"
    debug: bool = True
    log_level: str = "INFO"

    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_raw_events: str = "events.raw"
    kafka_topic_enriched_events: str = "events.enriched"
    kafka_topic_alerts: str = "events.alerts"
    kafka_consumer_group: str = "streampulse-processor"
    kafka_auto_offset_reset: str = "latest"
    kafka_session_timeout_ms: int = 30000
    kafka_heartbeat_interval_ms: int = 3000

    postgres_dsn: str = "postgresql+asyncpg://streampulse:password@localhost:5432/streampulse"

    clickhouse_host: str = "localhost"
    clickhouse_port: int = 8123
    clickhouse_user: str = "default"
    clickhouse_password: str = ""
    clickhouse_database: str = "streampulse"

    redis_url: str = "redis://localhost:6379/0"

    window_size_seconds: int = 60
    watermark_delay_seconds: int = 30
    max_batch_size: int = 1000
    commit_interval_seconds: int = 5

    anomaly_threshold_sigma: float = 3.0
    anomaly_window_seconds: int = 300
    baseline_window_seconds: int = 3600

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: list[str] = ["http://localhost:3000"]

    metrics_port: int = 9090
    health_check_interval_seconds: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()

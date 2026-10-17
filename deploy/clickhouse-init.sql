CREATE DATABASE IF NOT EXISTS streampulse;

CREATE TABLE IF NOT EXISTS streampulse.raw_events (
    event_id      String,
    event_type    LowCardinality(String),
    event_time    DateTime64(3, 'UTC'),
    user_id       String,
    session_id    String,
    page_url      String,
    referrer      String,
    device_type   LowCardinality(String),
    browser       LowCardinality(String),
    os            LowCardinality(String),
    country       LowCardinality(String),
    city          String,
    ip_hash       String,
    amount        Decimal64(2),
    currency      LowCardinality(String),
    properties    String,
    ingested_at   DateTime64(3, 'UTC'),
    processed_at  DateTime64(3, 'UTC')
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id, session_id)
TTL event_time + INTERVAL 90 DAY;

CREATE TABLE IF NOT EXISTS streampulse.enriched_events (
    event_id        String,
    event_type      LowCardinality(String),
    event_time      DateTime64(3, 'UTC'),
    user_id         String,
    session_id      String,
    page_url        String,
    referrer        String,
    device_type     LowCardinality(String),
    browser         LowCardinality(String),
    os              LowCardinality(String),
    country         LowCardinality(String),
    city            String,
    ip_hash         String,
    amount          Decimal64(2),
    currency        LowCardinality(String),
    properties      String,
    session_duration UInt32,
    page_sequence    UInt16,
    is_returning     UInt8,
    time_on_page_ms  UInt32,
    ingested_at     DateTime64(3, 'UTC'),
    processed_at    DateTime64(3, 'UTC')
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(event_time)
ORDER BY (event_time, user_id, session_id)
TTL event_time + INTERVAL 90 DAY;

CREATE TABLE IF NOT EXISTS streampulse.session_metrics (
    session_id      String,
    user_id         String,
    start_time      DateTime64(3, 'UTC'),
    end_time        DateTime64(3, 'UTC'),
    duration_sec    UInt32,
    page_count      UInt32,
    event_count     UInt32,
    total_revenue   Decimal64(2),
    device_type     LowCardinality(String),
    country         LowCardinality(String),
    top_page        String,
    referrer        String,
    updated_at      DateTime64(3, 'UTC')
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY (session_id, user_id);

CREATE TABLE IF NOT EXISTS streampulse.windowed_metrics (
    window_start    DateTime,
    window_type     LowCardinality(String),
    event_type      LowCardinality(String),
    metric_name     LowCardinality(String),
    metric_value    Float64,
    event_count     UInt32,
    unique_users    UInt32,
    computed_at     DateTime64(3, 'UTC')
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(window_start)
ORDER BY (window_start, window_type, event_type, metric_name);

CREATE TABLE IF NOT EXISTS streampulse.anomaly_alerts (
    alert_id        String,
    detected_at     DateTime64(3, 'UTC'),
    metric_name     LowCardinality(String),
    metric_value    Float64,
    expected_value  Float64,
    sigma_deviation Float64,
    window_seconds  UInt32,
    severity        LowCardinality(String),
    resolved        UInt8 DEFAULT 0,
    resolved_at     DateTime64(3, 'UTC') DEFAULT toDateTime64(0, 3, 'UTC')
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(detected_at)
ORDER BY (detected_at, metric_name);

CREATE TABLE IF NOT EXISTS streampulse.audit_log (
    log_id          String,
    timestamp       DateTime64(3, 'UTC'),
    component       LowCardinality(String),
    action          LowCardinality(String),
    status          LowCardinality(String),
    details         String,
    duration_ms     UInt32
) ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(timestamp)
ORDER BY (timestamp, component)
TTL timestamp + INTERVAL 30 DAY;

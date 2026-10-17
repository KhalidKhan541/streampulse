# StreamPulse API Reference

## Base URL
```
http://localhost:8000
```

## Endpoints

### GET /health
Returns service health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "streampulse-api",
  "timestamp": "2026-01-15T12:00:00Z",
  "uptime_seconds": 123.45
}
```

### GET /api/v1/metrics/summary
Returns aggregated metrics for a time window.

**Query Parameters:**
- `minutes` (int, default=60, min=1, max=1440) — time window in minutes

**Response:**
```json
{
  "total_events": 125000,
  "total_revenue": 45230.50,
  "active_sessions": 3421,
  "avg_session_duration": 185.2,
  "returning_user_ratio": 0.342,
  "top_pages": [{"page": "/products", "count": 1200}],
  "device_breakdown": {"desktop": 5000, "mobile": 4000},
  "country_breakdown": {"US": 6000, "GB": 2000},
  "anomaly_count_24h": 3
}
```

### GET /api/v1/metrics/timeseries
Returns time-series data for a metric.

**Query Parameters:**
- `metric` (string, default="total_events") — metric name
- `window_minutes` (int, default=5, min=1, max=1440)
- `limit` (int, default=120, min=1, max=1000)

**Response:**
```json
[
  {"timestamp": "2026-01-15T12:00:00Z", "value": 500, "label": "total_events"},
  {"timestamp": "2026-01-15T12:05:00Z", "value": 520, "label": "total_events"}
]
```

### GET /api/v1/anomalies
Returns recent anomaly alerts.

**Query Parameters:**
- `limit` (int, default=50, min=1, max=500)
- `severity` (string, optional) — filter by "info", "warning", or "critical"

**Response:**
```json
[
  {
    "alert_id": "abc-123",
    "detected_at": "2026-01-15T12:00:00Z",
    "metric_name": "total_events",
    "metric_value": 5000.0,
    "expected_value": 1000.0,
    "sigma_deviation": 4.5,
    "severity": "critical"
  }
]
```

### GET /api/v1/windows/closed
Returns recently closed tumbling windows.

**Query Parameters:**
- `limit` (int, default=20, min=1, max=200)

**Response:**
```json
[
  {
    "window_start": "2026-01-15T12:00:00Z",
    "window_type": "tumbling",
    "event_type": "all",
    "metric_name": "total_events",
    "metric_value": 500.0,
    "event_count": 500,
    "unique_users": 200
  }
]
```

from fastapi.testclient import TestClient

from streampulse.api.app import create_app


def test_health_endpoint():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "streampulse-api"


def test_metrics_summary():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/api/v1/metrics/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_events" in data
    assert "total_revenue" in data
    assert "active_sessions" in data


def test_metrics_summary_validation():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/api/v1/metrics/summary", params={"minutes": -1})
    assert resp.status_code == 422


def test_timeseries_endpoint():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/api/v1/metrics/timeseries", params={"metric": "total_events"})
    assert resp.status_code == 200


def test_anomalies_endpoint():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/api/v1/anomalies")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_closed_windows_endpoint():
    app = create_app()
    client = TestClient(app)
    resp = client.get("/api/v1/windows/closed")
    assert resp.status_code == 200

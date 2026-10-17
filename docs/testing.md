# StreamPulse Testing Guide

## Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# With coverage
pytest tests/ -v --cov=streampulse --cov-report=html

# Specific test
pytest tests/unit/test_enrichment.py::test_enrichment_basic -v
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures (raw_event, purchase_event, enriched_event)
├── unit/
│   ├── test_models.py       # Pydantic model validation tests
│   ├── test_enrichment.py   # EventEnricher tests
│   ├── test_aggregation.py  # TumblingWindowAggregator tests
│   ├── test_anomaly.py      # ZScoreAnomalyDetector tests
│   └── test_synthetic.py    # Synthetic event producer tests
└── integration/
    └── test_api.py          # FastAPI endpoint tests
```

## Test Categories

### Unit Tests
- **Models** — Pydantic schema validation, UTC enforcement, serialization round-trip
- **Enrichment** — session state, returning user detection, revenue accumulation, session cleanup
- **Aggregation** — window boundary logic, revenue tracking, unique user deduplication, metric conversion
- **Anomaly Detection** — spike/drop detection, severity classification, insufficient sample handling
- **Synthetic Producer** — deterministic output with seed, power user distribution, purchase amounts

### Integration Tests
- **API** — all endpoints return valid responses, input validation returns 422

## Writing New Tests

```python
def test_my_feature():
    # Arrange
    enricher = EventEnricher()
    
    # Act
    result = enricher.enrich(my_event)
    
    # Assert
    assert result.session_duration == 0
```

## CI Pipeline

Tests run in CI on every PR:
1. Lint (ruff + black)
2. Type check (mypy)
3. Unit + Integration tests (pytest with coverage)
4. Security scan (bandit + safety)
5. Docker build

from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.api import routes_health
from app.main import app


client = TestClient(app)


def test_health_check_is_application_liveness():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_check_succeeds_when_database_query_succeeds(monkeypatch):
    engine = create_engine("sqlite:///:memory:")
    monkeypatch.setattr(routes_health, "get_engine", lambda: engine)

    try:
        response = client.get("/ready")
    finally:
        engine.dispose()

    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "ok"}


def test_readiness_check_fails_when_database_is_unavailable(monkeypatch):
    def unavailable_engine():
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(routes_health, "get_engine", unavailable_engine)

    response = client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database is not ready"}

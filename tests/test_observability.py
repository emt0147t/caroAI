import re

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.observability import install_observability


def test_http_metrics_normalize_game_ids_and_expose_metrics_endpoint(monkeypatch):
    monkeypatch.setenv("CAROAI_METRICS_TOKEN", "phase-c-test-token")
    app = FastAPI()
    install_observability(app)

    @app.get("/api/games/{game_id}")
    def get_game(game_id: str):
        return {"id": game_id}

    with TestClient(app) as client:
        response = client.get("/api/games/12345678-1234-5678-1234-567812345678")
        metrics = client.get(
            "/metrics",
            headers={"Authorization": "Bearer phase-c-test-token"},
        )

    assert response.status_code == 200
    assert metrics.status_code == 200
    body = metrics.text
    assert 'route="/api/games/{game_id}"' in body
    assert "12345678-1234-5678-1234-567812345678" not in body
    assert "caroai_http_requests_total" in body


def test_metrics_endpoint_is_disabled_without_a_scrape_token(monkeypatch):
    monkeypatch.delenv("CAROAI_METRICS_TOKEN", raising=False)
    app = FastAPI()
    install_observability(app)

    with TestClient(app) as client:
        response = client.get("/metrics")

    assert response.status_code == 404


def test_metrics_endpoint_requires_matching_bearer_token(monkeypatch):
    monkeypatch.setenv("CAROAI_METRICS_TOKEN", "phase-c-test-token")
    app = FastAPI()
    install_observability(app)

    with TestClient(app) as client:
        missing = client.get("/metrics")
        wrong = client.get(
            "/metrics", headers={"Authorization": "Bearer wrong-token"}
        )
        valid = client.get(
            "/metrics",
            headers={"Authorization": "Bearer phase-c-test-token"},
        )

    assert missing.status_code == 401
    assert wrong.status_code == 401
    assert valid.status_code == 200


def test_metrics_endpoint_does_not_record_itself_as_application_traffic(
    monkeypatch,
):
    monkeypatch.setenv("CAROAI_METRICS_TOKEN", "phase-c-test-token")
    app = FastAPI()
    install_observability(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    with TestClient(app) as client:
        client.get("/health")
        body = client.get(
            "/metrics",
            headers={"Authorization": "Bearer phase-c-test-token"},
        ).text

    assert 'route="/metrics"' not in body
    assert 'route="/health"' in body

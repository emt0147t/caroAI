from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.observability import install_observability


def test_http_metrics_normalize_game_ids_and_expose_metrics_endpoint():
    app = FastAPI()
    install_observability(app)

    @app.get("/api/games/{game_id}")
    def get_game(game_id: str):
        return {"id": game_id}

    with TestClient(app) as client:
        response = client.get("/api/games/12345678-1234-5678-1234-567812345678")
        metrics = client.get("/metrics")

    assert response.status_code == 200
    assert metrics.status_code == 200
    body = metrics.text
    assert 'route="/api/games/{game_id}"' in body
    assert "12345678-1234-5678-1234-567812345678" not in body
    assert "caroai_http_requests_total" in body


def test_metrics_endpoint_does_not_record_itself_as_application_traffic():
    app = FastAPI()
    install_observability(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    with TestClient(app) as client:
        client.get("/health")
        body = client.get("/metrics").text

    assert 'route="/metrics"' not in body
    assert 'route="/health"' in body

import re
from uuid import uuid4

from fastapi.testclient import TestClient

from app.api.dependencies import get_game_service
from app.db.repository import InMemoryGameRepository
from app.main import app
from app.services.game_service import GameService


def test_qa_run_can_create_read_and_clean_only_its_own_games():
    repository = InMemoryGameRepository()

    def qa_service():
        yield GameService(repository)

    app.dependency_overrides[get_game_service] = qa_service
    run_id = uuid4().hex
    other_run_id = uuid4().hex
    headers = {"X-CaroAI-QA-Run-ID": run_id}
    other_headers = {"X-CaroAI-QA-Run-ID": other_run_id}

    try:
        with TestClient(app) as client:
            qa_created = client.post("/api/qa/games", headers=headers, json={
                "mode": "HUMAN_VS_HUMAN"
            })
            other_created = client.post("/api/qa/games", headers=other_headers, json={
                "mode": "HUMAN_VS_HUMAN"
            })
            assert qa_created.status_code == 201
            assert other_created.status_code == 201
            qa_id = qa_created.json()["id"]
            other_id = other_created.json()["id"]

            assert re.fullmatch(r"[0-9a-f]{32}", run_id)
            moved = client.post(
                f"/api/games/{qa_id}/moves", json={"row": 0, "col": 0}
            )
            assert moved.status_code == 200
            assert client.get(f"/api/games/{qa_id}").status_code == 200

            cleanup = client.delete("/api/qa/runs", headers=headers)
            assert cleanup.status_code == 200
            assert cleanup.json()["deleted_count"] == 1
            assert client.get(f"/api/games/{qa_id}").status_code == 404
            assert client.get(f"/api/games/{other_id}").status_code == 200

            other_cleanup = client.delete("/api/qa/runs", headers=other_headers)
            assert other_cleanup.status_code == 200
            assert other_cleanup.json()["deleted_count"] == 1
    finally:
        app.dependency_overrides.pop(get_game_service, None)


def test_qa_routes_reject_missing_or_invalid_run_capability():
    app.dependency_overrides[get_game_service] = lambda: GameService(
        InMemoryGameRepository()
    )
    try:
        with TestClient(app) as client:
            missing = client.post(
                "/api/qa/games", json={"mode": "HUMAN_VS_HUMAN"}
            )
            invalid = client.delete(
                "/api/qa/runs", headers={"X-CaroAI-QA-Run-ID": "not-a-run-id"}
            )
    finally:
        app.dependency_overrides.pop(get_game_service, None)

    assert missing.status_code == 422
    assert invalid.status_code == 422

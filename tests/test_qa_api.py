import time

from fastapi.testclient import TestClient

from app.api.dependencies import get_game_service
from app.api.qa_security import capability_for_run
from app.db.repository import InMemoryGameRepository
from app.domain.game_state import GameMode
from app.main import create_app
from app.services.game_service import GameService


SECRET_TEXT = "s" * 32
SECRET = SECRET_TEXT.encode("utf-8")


def make_client(monkeypatch, *, enabled=True):
    monkeypatch.setenv("CAROAI_QA_ENABLED", "true" if enabled else "false")
    monkeypatch.setenv("CAROAI_QA_HMAC_SECRET", SECRET_TEXT)
    repository = InMemoryGameRepository()
    application = create_app()
    application.dependency_overrides[get_game_service] = lambda: GameService(repository)
    return TestClient(application), repository


def auth_headers(run_id="a" * 32, *, secret=SECRET, expires_at=None):
    expiry = int(time.time()) + 60 if expires_at is None else expires_at
    return {
        "X-CaroAI-QA-Run-ID": run_id,
        "X-CaroAI-QA-Capability": capability_for_run(run_id, expiry, secret),
    }


def test_qa_routes_are_disabled_by_default_and_normal_games_still_work(monkeypatch):
    monkeypatch.delenv("CAROAI_QA_ENABLED", raising=False)
    monkeypatch.delenv("CAROAI_QA_HMAC_SECRET", raising=False)
    repository = InMemoryGameRepository()
    application = create_app()

    with TestClient(application) as client:
        disabled = client.post(
            "/api/qa/games", headers=auth_headers(), json={"mode": "HUMAN_VS_HUMAN"}
        )
        application.dependency_overrides[get_game_service] = lambda: GameService(
            repository
        )
        normal = client.post("/api/games", json={"mode": "HUMAN_VS_HUMAN"})

    assert disabled.status_code == 404
    assert normal.status_code == 201
    assert len(repository._games) == 1


def test_incomplete_qa_configuration_returns_404_without_service_access(monkeypatch):
    monkeypatch.setenv("CAROAI_QA_ENABLED", "true")
    monkeypatch.delenv("CAROAI_QA_HMAC_SECRET", raising=False)
    repository = InMemoryGameRepository()
    application = create_app()
    with TestClient(application) as client:
        response = client.post(
            "/api/qa/games", headers=auth_headers(), json={"mode": "HUMAN_VS_HUMAN"}
        )

    assert response.status_code == 404
    assert repository._games == {}


def test_qa_create_and_cleanup_reject_missing_malformed_expired_and_wrong_scope(
    monkeypatch,
):
    client, repository = make_client(monkeypatch, enabled=True)
    run_id = "a" * 32
    wrong_scope = {
        **auth_headers("b" * 32),
        "X-CaroAI-QA-Run-ID": run_id,
    }
    expired = auth_headers(run_id, expires_at=int(time.time()) - 1)
    tampered = auth_headers(run_id)
    tampered["X-CaroAI-QA-Capability"] = (
        tampered["X-CaroAI-QA-Capability"][:-1]
        + ("0" if tampered["X-CaroAI-QA-Capability"][-1] != "0" else "1")
    )

    with client:
        create_missing = client.post(
            "/api/qa/games",
            headers={"X-CaroAI-QA-Run-ID": run_id},
            json={"mode": "HUMAN_VS_HUMAN"},
        )
        cleanup_missing = client.delete(
            "/api/qa/runs", headers={"X-CaroAI-QA-Run-ID": run_id}
        )
        create_malformed = client.post(
            "/api/qa/games",
            headers={
                "X-CaroAI-QA-Run-ID": run_id,
                "X-CaroAI-QA-Capability": "not-a-capability",
            },
            json={"mode": "HUMAN_VS_HUMAN"},
        )
        cleanup_malformed = client.delete(
            "/api/qa/runs",
            headers={**auth_headers(run_id), "X-CaroAI-QA-Capability": "bad"},
        )
        create_expired = client.post(
            "/api/qa/games",
            headers=expired,
            json={"mode": "HUMAN_VS_HUMAN"},
        )
        create_tampered = client.post(
            "/api/qa/games",
            headers=tampered,
            json={"mode": "HUMAN_VS_HUMAN"},
        )
        create_wrong_scope = client.post(
            "/api/qa/games",
            headers=wrong_scope,
            json={"mode": "HUMAN_VS_HUMAN"},
        )
        cleanup_wrong_scope = client.delete("/api/qa/runs", headers=wrong_scope)

    assert all(
        response.status_code == 401
        for response in (
            create_missing,
            cleanup_missing,
            create_malformed,
            cleanup_malformed,
            create_expired,
            create_tampered,
            create_wrong_scope,
            cleanup_wrong_scope,
        )
    )
    assert repository._games == {}


def test_valid_capability_creates_and_cleans_only_its_run(monkeypatch):
    client, repository = make_client(monkeypatch, enabled=True)
    run_a = "a" * 32
    run_b = "b" * 32

    with client:
        created_a = client.post(
            "/api/qa/games",
            headers=auth_headers(run_a),
            json={"mode": "HUMAN_VS_HUMAN"},
        )
        created_b = client.post(
            "/api/qa/games",
            headers=auth_headers(run_b),
            json={"mode": "HUMAN_VS_HUMAN"},
        )
        ordinary = GameService(repository).create_game(GameMode.HUMAN_VS_HUMAN)
        unauthorized_cleanup = client.delete(
            "/api/qa/runs",
            headers={
                "X-CaroAI-QA-Run-ID": run_a,
                "X-CaroAI-QA-Capability": auth_headers(run_b)[
                    "X-CaroAI-QA-Capability"
                ],
            },
        )
        cleanup_a = client.delete("/api/qa/runs", headers=auth_headers(run_a))
        cleanup_a_again = client.delete("/api/qa/runs", headers=auth_headers(run_a))

    assert created_a.status_code == created_b.status_code == 201
    assert unauthorized_cleanup.status_code == 401
    assert cleanup_a.status_code == cleanup_a_again.status_code == 200
    assert cleanup_a.json()["deleted_count"] == 1
    assert cleanup_a_again.json()["deleted_count"] == 0
    assert created_a.json()["id"] not in repository._games
    assert created_b.json()["id"] in repository._games
    assert ordinary in repository._games


def test_per_run_game_limit_is_not_reset_by_cleanup(monkeypatch):
    client, repository = make_client(monkeypatch, enabled=True)
    headers = auth_headers("c" * 32)

    with client:
        first = client.post(
            "/api/qa/games", headers=headers, json={"mode": "HUMAN_VS_HUMAN"}
        )
        second = client.post(
            "/api/qa/games", headers=headers, json={"mode": "HUMAN_VS_HUMAN"}
        )
        client.delete("/api/qa/runs", headers=headers)
        third = client.post(
            "/api/qa/games", headers=headers, json={"mode": "HUMAN_VS_HUMAN"}
        )

    assert first.status_code == second.status_code == 201
    assert third.status_code == 429
    assert repository._games == {}


def test_qa_rate_limit_is_separate_from_normal_gameplay(monkeypatch):
    client, _repository = make_client(monkeypatch, enabled=True)
    headers = auth_headers("d" * 32)

    with client:
        responses = [
            client.delete("/api/qa/runs", headers=headers) for _ in range(11)
        ]
        ordinary = client.post("/api/games", json={"mode": "HUMAN_VS_HUMAN"})

    assert [response.status_code for response in responses] == [
        200
    ] * 10 + [429]
    assert ordinary.status_code == 201


def test_capability_never_appears_in_api_response_or_logs(monkeypatch, capsys):
    client, _repository = make_client(monkeypatch, enabled=True)
    headers = auth_headers("e" * 32)
    capability = headers["X-CaroAI-QA-Capability"]

    with client:
        response = client.post(
            "/api/qa/games",
            headers=headers,
            json={"mode": "HUMAN_VS_HUMAN"},
        )
    captured = capsys.readouterr()

    assert response.status_code == 201
    assert capability not in response.text
    assert capability not in captured.out
    assert capability not in captured.err

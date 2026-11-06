"""Tests for the controlled production PvP/PvAI acceptance runner."""

from __future__ import annotations

from scripts import production_qa_acceptance as qa


RUN_ID = "a" * 32
PVP_ID = "qa-pvp-game"
PVAI_ID = "qa-pvai-game"


def install_fake_acceptance_api(monkeypatch, *, fail_ai: bool = False):
    """Replace HTTP calls with a deterministic API/DB acceptance harness."""
    state = {
        "pvp_moves": 0,
        "deleted": False,
        "calls": [],
    }

    def create_qa_game(payload, _expected_status):
        game_id = PVP_ID if payload["mode"] == "HUMAN_VS_HUMAN" else PVAI_ID
        return 201, {
            "id": game_id,
            "mode": payload["mode"],
            "move_count": 0,
        }

    def post_pvp_move(_payload, _expected_status):
        state["pvp_moves"] += 1
        count = state["pvp_moves"]
        terminal = count == 9
        return 200, {
            "game": {
                "mode": "HUMAN_VS_HUMAN",
                "status": "X_WON" if terminal else "IN_PROGRESS",
                "winner": "X" if terminal else None,
                "move_count": count,
            }
        }

    def post_pvai_human_move(_payload, _expected_status):
        return 200, {"game": {"current_player": "O", "move_count": 1}}

    def post_pvai_ai_move(_payload, _expected_status):
        if fail_ai:
            raise qa.AcceptanceError("simulated AI endpoint failure")
        board = [["EMPTY"] * 15 for _ in range(15)]
        board[7][7] = "X"
        board[7][8] = "O"
        return 200, {
            "move": {"row": 7, "col": 8, "player": "O"},
            "game": {
                "mode": "HUMAN_VS_AI",
                "status": "IN_PROGRESS",
                "current_player": "X",
                "move_count": 2,
                "board": board,
            },
        }

    def get_pvp_detail(_payload, expected_status):
        if state["deleted"]:
            return 404, {}
        return 200, {
            "id": PVP_ID,
            "mode": "HUMAN_VS_HUMAN",
            "status": "X_WON",
            "winner": "X",
            "move_count": 9,
        }

    def get_pvai_detail(_payload, expected_status):
        if state["deleted"]:
            return 404, {}
        return 200, {
            "id": PVAI_ID,
            "mode": "HUMAN_VS_AI",
            "status": "IN_PROGRESS",
            "current_player": "X",
            "move_count": 2,
        }

    def get_history(_payload, _expected_status):
        if state["deleted"]:
            return 200, {"items": []}
        return 200, {
            "items": [
                {
                    "id": PVP_ID,
                    "mode": "HUMAN_VS_HUMAN",
                    "status": "X_WON",
                    "result": "X_WON",
                    "move_count": 9,
                },
                {
                    "id": PVAI_ID,
                    "mode": "HUMAN_VS_AI",
                    "status": "IN_PROGRESS",
                    "result": None,
                    "move_count": 2,
                },
            ]
        }

    def delete_qa_run(_payload, _expected_status):
        state["deleted"] = True
        return 200, {
            "deleted_count": 2,
            "deleted_game_ids": [PVP_ID, PVAI_ID],
        }

    handlers = {
        ("POST", "/api/qa/games"): create_qa_game,
        ("POST", f"/api/games/{PVP_ID}/moves"): post_pvp_move,
        ("POST", f"/api/games/{PVAI_ID}/moves"): post_pvai_human_move,
        ("POST", f"/api/games/{PVAI_ID}/ai-move"): post_pvai_ai_move,
        ("GET", f"/api/games/{PVP_ID}"): get_pvp_detail,
        ("GET", f"/api/games/{PVAI_ID}"): get_pvai_detail,
        ("GET", "/api/history?limit=100&offset=0"): get_history,
        ("DELETE", "/api/qa/runs"): delete_qa_run,
    }

    def fake_request_json(
        base_url,
        method,
        path,
        *,
        run_id,
        payload=None,
        expected_status=(200,),
    ):
        assert base_url == "https://caroai.example"
        assert run_id == RUN_ID
        state["calls"].append((method, path, payload, expected_status))
        handler = handlers.get((method, path))
        if handler is None:
            raise AssertionError(f"Unexpected acceptance request: {method} {path}")
        return handler(payload, expected_status)

    monkeypatch.setenv("CAROAI_PUBLIC_URL", "https://caroai.example")
    monkeypatch.setattr(qa.secrets, "token_hex", lambda _size: RUN_ID)
    monkeypatch.setattr(qa, "request_json", fake_request_json)
    return state


def test_production_acceptance_runs_pvp_pvai_reads_history_and_cleans(monkeypatch):
    state = install_fake_acceptance_api(monkeypatch)

    assert qa.main() == 0
    assert state["pvp_moves"] == 9
    assert state["deleted"] is True
    assert any(
        method == "DELETE" and path == "/api/qa/runs"
        for method, path, _payload, _expected in state["calls"]
    )
    # Each game is checked for HTTP 404 after cleanup.
    deleted_reads = [
        expected
        for method, path, _payload, expected in state["calls"]
        if method == "GET"
        and path in {f"/api/games/{PVP_ID}", f"/api/games/{PVAI_ID}"}
        and expected == (404,)
    ]
    assert len(deleted_reads) == 2


def test_production_acceptance_cleans_both_games_when_pvai_fails(
    monkeypatch, capsys
):
    state = install_fake_acceptance_api(monkeypatch, fail_ai=True)

    assert qa.main() == 1
    assert state["deleted"] is True
    output = capsys.readouterr()
    assert "Production gameplay acceptance failed" in output.err
    assert "Production QA cleanup verified" in output.out

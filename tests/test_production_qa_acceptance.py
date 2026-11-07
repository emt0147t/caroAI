"""Tests for the controlled production PvP/PvAI acceptance runner."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from app.api.qa_security import verify_capability
from scripts import production_qa_acceptance as qa


RUN_ID = "a" * 32
SECRET = "s" * 32
PVP_ID = "qa-pvp-game"
PVAI_ID = "qa-pvai-game"


class FakeAcceptanceAPI:
    """Small in-memory API stub used to exercise the acceptance script."""

    def __init__(self, *, fail_ai: bool = False):
        self.fail_ai = fail_ai
        self.state = {"pvp_moves": 0, "deleted": False, "calls": []}
        self.handlers = {
            ("POST", "/api/qa/games"): self.create_qa_game,
            ("POST", f"/api/games/{PVP_ID}/moves"): self.post_pvp_move,
            ("POST", f"/api/games/{PVAI_ID}/moves"): self.post_pvai_human_move,
            ("POST", f"/api/games/{PVAI_ID}/ai-move"): self.post_pvai_ai_move,
            ("GET", f"/api/games/{PVP_ID}"): self.get_pvp_detail,
            ("GET", f"/api/games/{PVAI_ID}"): self.get_pvai_detail,
            ("GET", "/api/history?limit=100&offset=0"): self.get_history,
            ("DELETE", "/api/qa/runs"): self.delete_qa_run,
        }

    def __call__(
        self,
        base_url,
        method,
        path,
        *,
        run_id,
        capability,
        payload=None,
        expected_status=(200,),
    ):
        assert base_url == "https://caroai.example"
        assert run_id == RUN_ID
        assert verify_capability(
            run_id, capability, SECRET.encode(), now=int(time.time())
        )
        self.state["calls"].append(
            (method, path, payload, expected_status, capability)
        )
        handler = self.handlers.get((method, path))
        if handler is None:
            raise AssertionError(f"Unexpected acceptance request: {method} {path}")
        return handler(payload, expected_status)

    def create_qa_game(self, payload, _expected_status):
        game_id = PVP_ID if payload["mode"] == "HUMAN_VS_HUMAN" else PVAI_ID
        return 201, {
            "id": game_id,
            "mode": payload["mode"],
            "move_count": 0,
        }

    def post_pvp_move(self, _payload, _expected_status):
        self.state["pvp_moves"] += 1
        count = self.state["pvp_moves"]
        terminal = count == 9
        return 200, {
            "game": {
                "mode": "HUMAN_VS_HUMAN",
                "status": "X_WON" if terminal else "IN_PROGRESS",
                "winner": "X" if terminal else None,
                "move_count": count,
            }
        }

    def post_pvai_human_move(self, _payload, _expected_status):
        return 200, {"game": {"current_player": "O", "move_count": 1}}

    def post_pvai_ai_move(self, _payload, _expected_status):
        if self.fail_ai:
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

    def get_pvp_detail(self, _payload, _expected_status):
        if self.state["deleted"]:
            return 404, {}
        return 200, {
            "id": PVP_ID,
            "mode": "HUMAN_VS_HUMAN",
            "status": "X_WON",
            "winner": "X",
            "move_count": 9,
        }

    def get_pvai_detail(self, _payload, _expected_status):
        if self.state["deleted"]:
            return 404, {}
        return 200, {
            "id": PVAI_ID,
            "mode": "HUMAN_VS_AI",
            "status": "IN_PROGRESS",
            "current_player": "X",
            "move_count": 2,
        }

    def get_history(self, _payload, _expected_status):
        if self.state["deleted"]:
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

    def delete_qa_run(self, _payload, _expected_status):
        self.state["deleted"] = True
        return 200, {
            "deleted_count": 2,
            "deleted_game_ids": [PVP_ID, PVAI_ID],
        }


def install_fake_acceptance_api(monkeypatch, *, fail_ai: bool = False):
    """Patch the runner to use an isolated fake HTTPS endpoint."""
    stub = FakeAcceptanceAPI(fail_ai=fail_ai)
    monkeypatch.setenv("CAROAI_PUBLIC_URL", "https://caroai.example")
    monkeypatch.setenv("CAROAI_QA_HMAC_SECRET", SECRET)
    monkeypatch.setattr(qa.secrets, "token_hex", lambda _size: RUN_ID)
    monkeypatch.setattr(qa, "request_json", stub)
    return stub.state


def test_production_acceptance_runs_pvp_pvai_reads_history_and_cleans(
    monkeypatch, capsys
):
    state = install_fake_acceptance_api(monkeypatch)

    assert qa.main([]) == 0
    assert state["pvp_moves"] == 9
    assert state["deleted"] is True
    assert any(
        method == "DELETE" and path == "/api/qa/runs"
        for method, path, _payload, _expected, _capability in state["calls"]
    )
    # Each game is checked for HTTP 404 after cleanup.
    deleted_reads = [
        expected
        for method, path, _payload, expected, _capability in state["calls"]
        if method == "GET"
        and path in {f"/api/games/{PVP_ID}", f"/api/games/{PVAI_ID}"}
        and expected == (404,)
    ]
    assert len(deleted_reads) == 2
    output = capsys.readouterr()
    assert all(
        capability not in output.out + output.err
        for _method, _path, _payload, _expected, capability in state["calls"]
    )


def test_production_acceptance_cleans_both_games_when_pvai_fails(
    monkeypatch, capsys
):
    state = install_fake_acceptance_api(monkeypatch, fail_ai=True)

    assert qa.main([]) == 1
    assert state["deleted"] is True
    output = capsys.readouterr()
    assert "Production gameplay acceptance failed" in output.err
    assert "Production QA cleanup verified" in output.out


def test_production_acceptance_requires_hmac_secret_before_api_calls(monkeypatch):
    monkeypatch.setenv("CAROAI_PUBLIC_URL", "https://caroai.example")
    monkeypatch.delenv("CAROAI_QA_HMAC_SECRET", raising=False)
    monkeypatch.setattr(qa.secrets, "token_hex", lambda _size: RUN_ID)

    try:
        qa.main([])
    except SystemExit as exc:
        assert "CAROAI_QA_HMAC_SECRET" in str(exc)
    else:
        raise AssertionError("acceptance runner should require its signing secret")


def test_production_acceptance_can_retry_exact_run_cleanup(monkeypatch, capsys):
    state = install_fake_acceptance_api(monkeypatch)

    assert qa.main(["--cleanup-run-id", RUN_ID]) == 0
    output = capsys.readouterr()
    assert state["deleted"] is True
    assert "recovery cleanup verified" in output.out
    assert all(
        capability not in output.out + output.err
        for _method, _path, _payload, _expected, capability in state["calls"]
    )
    assert all(method != "POST" for method, *_rest in state["calls"])


def test_production_acceptance_script_help_works_outside_repo_without_pythonpath(tmp_path):
    script_path = Path(qa.__file__).resolve()
    result = subprocess.run(
        [sys.executable, "-I", str(script_path), "--help"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "--cleanup-run-id" in result.stdout

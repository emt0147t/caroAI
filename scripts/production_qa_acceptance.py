"""Controlled production PvP/PvAI acceptance with exact-run cleanup.

This script is invoked only by the approved production release job after the
new image is confirmed live. It creates two explicitly tagged QA games, verifies
the authoritative API and history reads, and deletes only its own run's games.
"""

from __future__ import annotations

import json
import os
import secrets
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


TIMEOUT_SECONDS = 20


class AcceptanceError(RuntimeError):
    """Raised when a production gameplay acceptance assertion fails."""


def request_json(
    base_url: str,
    method: str,
    path: str,
    *,
    run_id: str,
    payload: dict | None = None,
    expected_status: tuple[int, ...] = (200,),
) -> tuple[int, dict]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"X-CaroAI-QA-Run-ID": run_id, "Accept": "application/json"}
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = Request(
        base_url.rstrip("/") + path,
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = response.status
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        status = exc.code
        raw = exc.read().decode("utf-8", errors="replace")
    except URLError as exc:
        raise AcceptanceError(f"{method} {path} transport failed: {exc.reason}") from exc

    try:
        parsed = json.loads(raw) if raw else {}
    except json.JSONDecodeError as exc:
        raise AcceptanceError(
            f"{method} {path} returned non-JSON data (HTTP {status})"
        ) from exc
    if status not in expected_status:
        detail = parsed.get("detail", "no detail") if isinstance(parsed, dict) else "invalid body"
        raise AcceptanceError(
            f"{method} {path} expected {expected_status}, received HTTP {status}: {detail}"
        )
    if not isinstance(parsed, dict):
        raise AcceptanceError(f"{method} {path} returned a non-object JSON value")
    return status, parsed


def create_qa_game(base_url: str, run_id: str, mode: str) -> str:
    _status, payload = request_json(
        base_url,
        "POST",
        "/api/qa/games",
        run_id=run_id,
        payload={"mode": mode},
        expected_status=(201,),
    )
    game_id = payload.get("id")
    if not isinstance(game_id, str) or not game_id:
        raise AcceptanceError("QA game creation did not return a public game ID")
    if payload.get("mode") != mode or payload.get("move_count") != 0:
        raise AcceptanceError("QA game creation returned an unexpected initial state")
    return game_id


def play_pvp_win(base_url: str, run_id: str, game_id: str) -> None:
    # X completes a horizontal five; O replies in a separate row.
    moves = [
        (0, 0), (1, 0),
        (0, 1), (1, 1),
        (0, 2), (1, 2),
        (0, 3), (1, 3),
        (0, 4),
    ]
    last = {}
    for row, col in moves:
        _status, last = request_json(
            base_url,
            "POST",
            f"/api/games/{game_id}/moves",
            run_id=run_id,
            payload={"row": row, "col": col},
        )
    game = last.get("game", {})
    if (
        game.get("status") != "X_WON"
        or game.get("winner") != "X"
        or game.get("move_count") != 9
    ):
        raise AcceptanceError("PvP did not persist the expected X_WON terminal state")


def play_pvai_turn(base_url: str, run_id: str, game_id: str) -> None:
    _status, human = request_json(
        base_url,
        "POST",
        f"/api/games/{game_id}/moves",
        run_id=run_id,
        payload={"row": 7, "col": 7},
    )
    if human.get("game", {}).get("current_player") != "O":
        raise AcceptanceError("PvAI human move did not pass control to O")

    _status, ai = request_json(
        base_url,
        "POST",
        f"/api/games/{game_id}/ai-move",
        run_id=run_id,
        payload={"difficulty": "medium"},
    )
    move = ai.get("move", {})
    state = ai.get("game", {})
    if move.get("player") != "O" or state.get("move_count") != 2:
        raise AcceptanceError("PvAI response did not persist one legal AI move")
    if not (0 <= int(move.get("row", -1)) < 15 and 0 <= int(move.get("col", -1)) < 15):
        raise AcceptanceError("PvAI returned coordinates outside the board")


def verify_fresh_reads_and_history(
    base_url: str, run_id: str, game_ids: list[str]
) -> None:
    for game_id in game_ids:
        _status, detail = request_json(
            base_url, "GET", f"/api/games/{game_id}", run_id=run_id
        )
        if detail.get("id") != game_id:
            raise AcceptanceError("Fresh game-detail read returned a different game")

    _status, history = request_json(
        base_url,
        "GET",
        "/api/history?limit=100&offset=0",
        run_id=run_id,
    )
    history_ids = {item.get("id") for item in history.get("items", [])}
    missing = set(game_ids) - history_ids
    if missing:
        raise AcceptanceError("QA games were not visible in the persisted history read")


def cleanup_and_verify(base_url: str, run_id: str, game_ids: list[str]) -> None:
    _status, result = request_json(
        base_url,
        "DELETE",
        "/api/qa/runs",
        run_id=run_id,
    )
    deleted_ids = set(result.get("deleted_game_ids", []))
    if not set(game_ids).issubset(deleted_ids):
        raise AcceptanceError("QA cleanup did not report all games created by this run")

    for game_id in game_ids:
        request_json(
            base_url,
            "GET",
            f"/api/games/{game_id}",
            run_id=run_id,
            expected_status=(404,),
        )

    _status, history = request_json(
        base_url,
        "GET",
        "/api/history?limit=100&offset=0",
        run_id=run_id,
    )
    history_ids = {item.get("id") for item in history.get("items", [])}
    if history_ids.intersection(game_ids):
        raise AcceptanceError("Cleaned QA games are still visible in game history")


def main() -> int:
    base_url = os.getenv("CAROAI_PUBLIC_URL", "").rstrip("/")
    if not base_url.startswith("https://"):
        raise SystemExit("CAROAI_PUBLIC_URL must be a configured public HTTPS URL")

    run_id = secrets.token_hex(16)
    game_ids: list[str] = []
    primary_error = None
    cleanup_error = None

    try:
        pvp_id = create_qa_game(base_url, run_id, "HUMAN_VS_HUMAN")
        game_ids.append(pvp_id)
        pvai_id = create_qa_game(base_url, run_id, "HUMAN_VS_AI")
        game_ids.append(pvai_id)

        play_pvp_win(base_url, run_id, pvp_id)
        play_pvai_turn(base_url, run_id, pvai_id)
        verify_fresh_reads_and_history(base_url, run_id, game_ids)
        print("Production gameplay acceptance passed: PvP win, PvAI move, fresh reads and history.")
    except Exception as exc:
        primary_error = exc
    finally:
        try:
            # Cleanup is required even when a gameplay assertion fails halfway.
            cleanup_and_verify(base_url, run_id, game_ids)
            print("Production QA cleanup verified: run-scoped records deleted.")
        except Exception as exc:
            cleanup_error = exc

    if cleanup_error is not None:
        # The capability is printed only when an operator needs it for exact-run recovery.
        print(
            f"CRITICAL: QA cleanup failed ({cleanup_error}). "
            f"Run capability for narrow cleanup recovery: {run_id}",
            file=sys.stderr,
        )
        return 2
    if primary_error is not None:
        print(f"Production gameplay acceptance failed: {primary_error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

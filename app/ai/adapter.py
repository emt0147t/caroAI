"""Adapters between Backend board values and the AI engine representation.

Backend is authoritative and represents cells as EMPTY, X and O.
The Sprint 1 AI engine uses integer cells 0, 1 and 2.
"""
from app.domain.game_state import BOARD_SIZE

BACKEND_TO_AI = {
    "EMPTY": 0,
    "X": 1,
    "O": 2,
}

AI_TO_BACKEND = {value: key for key, value in BACKEND_TO_AI.items()}


def board_to_ai(board: list[list[str]]) -> list[list[int]]:
    """Return an independent AI-compatible snapshot of a backend board."""
    if len(board) != BOARD_SIZE or any(
        len(row) != BOARD_SIZE for row in board
    ):
        raise ValueError(f"Board must be {BOARD_SIZE}x{BOARD_SIZE}")

    try:
        return [[BACKEND_TO_AI[cell] for cell in row] for row in board]
    except KeyError as exc:
        raise ValueError(f"Unknown backend board value: {exc.args[0]}") from exc


def board_from_ai(board: list[list[int]]) -> list[list[str]]:
    """Convert an AI board into an independent Backend board snapshot."""
    if len(board) != BOARD_SIZE or any(
        len(row) != BOARD_SIZE for row in board
    ):
        raise ValueError(f"Board must be {BOARD_SIZE}x{BOARD_SIZE}")

    try:
        return [[AI_TO_BACKEND[cell] for cell in row] for row in board]
    except KeyError as exc:
        raise ValueError(f"Unknown AI board value: {exc.args[0]}") from exc

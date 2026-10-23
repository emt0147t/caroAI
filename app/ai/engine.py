import time
from typing import Any, Dict, List

from app.ai.evaluator import BOARD_SIZE, EMPTY
from app.ai.minimax import find_best_move

DIFFICULTY_CONFIG = {
    "EASY": {"depth": 1, "candidate_limit": 6},
    "MEDIUM": {"depth": 2, "candidate_limit": 10},
    "HARD": {"depth": 3, "candidate_limit": 14},
}


def _validate_engine_move(board: List[List[int]], row: Any, col: Any, score: Any) -> None:
    """Fail closed if the search ever returns a malformed or illegal move."""
    if (
        not isinstance(row, int)
        or isinstance(row, bool)
        or not isinstance(col, int)
        or isinstance(col, bool)
    ):
        raise ValueError("AI engine returned malformed move coordinates")
    if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
        raise ValueError("AI engine returned an out-of-bounds move")
    if board[row][col] != EMPTY:
        raise ValueError("AI engine returned a move on an occupied cell")
    if not isinstance(score, int) or isinstance(score, bool):
        raise ValueError("AI engine returned a malformed score")


def get_ai_move(
    board: List[List[int]],
    ai_player: int,
    difficulty: str = "MEDIUM",
) -> Dict[str, Any]:
    """
    Entry point chính của AI Engine để Backend FastAPI gọi tới.

    Difficulty giữ nguyên contract Sprint 2: case-insensitive và fallback MEDIUM
    khi giá trị dạng chuỗi không nằm trong cấu hình. Không có candidate hợp lệ
    hoặc search trả output bất hợp lệ sẽ raise ValueError thay vì giả trả nước đi.
    """
    if not isinstance(difficulty, str):
        raise ValueError("AI difficulty must be a string")

    diff_key = difficulty.upper()
    config = DIFFICULTY_CONFIG.get(diff_key, DIFFICULTY_CONFIG["MEDIUM"])

    start_time = time.perf_counter()
    (row, col), score = find_best_move(
        board=board,
        ai_player=ai_player,
        depth=config["depth"],
        candidate_limit=config["candidate_limit"],
    )
    _validate_engine_move(board, row, col, score)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "row": row,
        "col": col,
        "score": score,
        "elapsed_ms": round(elapsed_ms, 2),
    }

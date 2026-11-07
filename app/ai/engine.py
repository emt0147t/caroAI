import math
import os
import time
from typing import Any, Dict, List

from app.ai.evaluator import BOARD_SIZE, EMPTY
from app.ai.minimax import find_best_move
from app.ai.search_stats import SearchStats
from app.ai.competitive import POLICIES, choose_move

DIFFICULTY_CONFIG = {
    "EASY": {"depth": 1, "candidate_limit": 6},
    "MEDIUM": {"depth": 2, "candidate_limit": 10},
    **{
        level: {
            "depth": policy.depth,
            "candidate_limit": policy.quiet_limit,
            "radius": policy.radius,
            "extensions": policy.extensions,
            "proof_depth": policy.proof_depth,
            "time_budget_ms": policy.time_ms,
            "node_budget": policy.node_limit,
        }
        for level, policy in POLICIES.items() if level in {"HARD", "IMPOSSIBLE"}
    },
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


def get_ai_move(  # noqa: C901
    board: List[List[int]],
    ai_player: int,
    difficulty: str = "MEDIUM",
    *,
    time_budget_ms: float | None = None,
    collect_stats: bool = True,
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

    if time_budget_ms is None and diff_key == "IMPOSSIBLE":
        configured_budget = os.getenv("CAROAI_IMPOSSIBLE_TIME_BUDGET_MS")
        if configured_budget:
            try:
                time_budget_ms = float(configured_budget)
            except ValueError as exc:
                raise ValueError(
                    "CAROAI_IMPOSSIBLE_TIME_BUDGET_MS must be numeric"
                ) from exc

    if time_budget_ms is not None and (not math.isfinite(time_budget_ms) or time_budget_ms < 0):
        raise ValueError("time_budget_ms must be non-negative")

    start_time = time.perf_counter()
    if diff_key in {"HARD", "IMPOSSIBLE"}:
        result = choose_move(board, ai_player, POLICIES[diff_key], time_budget_ms=time_budget_ms)
        if not collect_stats:
            result.pop("search_stats", None)
    else:
        stats = SearchStats() if (collect_stats or time_budget_ms is not None) else None
        (row, col), score = find_best_move(
            board=board,
            ai_player=ai_player,
            depth=config["depth"],
            candidate_limit=config["candidate_limit"],
            stats=stats,
            time_budget_ms=time_budget_ms,
        )
        result = {"row": row, "col": col, "score": score}
        if collect_stats and stats is not None:
            result["search_stats"] = stats.to_dict()

    _validate_engine_move(board, result["row"], result["col"], result["score"])
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    result["elapsed_ms"] = round(elapsed_ms, 3)
    if "search_stats" in result:
        result["search_stats"]["elapsed_ms"] = elapsed_ms
    return result

import math
import os
import time
from typing import Any, Dict, List

from app.ai.evaluator import BOARD_SIZE, EMPTY
from app.ai.minimax import find_best_move
from app.ai.search_stats import SearchStats
from app.ai.strategic_search import find_strategic_move


DIFFICULTY_CONFIG = {
    "EASY": {"depth": 1, "candidate_limit": 6},
    "MEDIUM": {"depth": 2, "candidate_limit": 10},
    "HARD": {
        "depth": 5,
        "candidate_limit": 8,
        "time_budget_ms": 250,
        "node_budget": 16000,
        "diversify": True,
    },
    "IMPOSSIBLE": {
        "depth": 8,
        "candidate_limit": 10,
        "time_budget_ms": 700,
        "node_budget": 40000,
        "diversify": True,
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
    """Backend-compatible AI entry point with bounded strategic modes."""
    if not isinstance(difficulty, str):
        raise ValueError("AI difficulty must be a string")

    diff_key = difficulty.upper()
    config = DIFFICULTY_CONFIG.get(diff_key, DIFFICULTY_CONFIG["MEDIUM"])

    # Keep the existing environment override and default hard-level budgets.
    if diff_key == "IMPOSSIBLE" and time_budget_ms is None:
        configured_budget = os.getenv("CAROAI_IMPOSSIBLE_TIME_BUDGET_MS")
        if configured_budget:
            try:
                time_budget_ms = float(configured_budget)
            except ValueError as exc:
                raise ValueError(
                    "CAROAI_IMPOSSIBLE_TIME_BUDGET_MS must be numeric"
                ) from exc
    if diff_key in {"HARD", "IMPOSSIBLE"} and time_budget_ms is None:
        time_budget_ms = float(config["time_budget_ms"])

    if time_budget_ms is not None and (
        not math.isfinite(time_budget_ms) or time_budget_ms < 0
    ):
        raise ValueError("time_budget_ms must be non-negative")

    stats = SearchStats() if (collect_stats or time_budget_ms is not None) else None
    start_time = time.perf_counter()

    if diff_key in {"HARD", "IMPOSSIBLE"}:
        budget = int(
            time_budget_ms if time_budget_ms is not None else config["time_budget_ms"]
        )
        (row, col), score, search_info = find_strategic_move(
            board=board,
            ai_player=ai_player,
            max_depth=config["depth"],
            candidate_limit=config["candidate_limit"],
            time_budget_ms=budget,
            node_budget=config["node_budget"],
            diversify=config["diversify"],
            stats=stats,
        )
    else:
        (row, col), score = find_best_move(
            board=board,
            ai_player=ai_player,
            depth=config["depth"],
            candidate_limit=config["candidate_limit"],
            stats=stats,
            time_budget_ms=time_budget_ms,
        )
        search_info = {}

    _validate_engine_move(board, row, col, score)
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0
    if stats is not None:
        stats.elapsed_ms = elapsed_ms

    result = {
        "row": row,
        "col": col,
        "score": score,
        "elapsed_ms": round(elapsed_ms, 2),
    }
    if collect_stats and stats is not None:
        result["search_stats"] = stats.to_dict()
        result["search_stats"].update(search_info)
    return result

import time
from typing import List, Dict, Any
from app.ai.minimax import find_best_move

DIFFICULTY_CONFIG = {
    "EASY": {"depth": 1, "candidate_limit": 6},
    "MEDIUM": {"depth": 2, "candidate_limit": 10},
    "HARD": {"depth": 3, "candidate_limit": 14}
}

def get_ai_move(
    board: List[List[int]],
    ai_player: int,
    difficulty: str = "MEDIUM"
) -> Dict[str, Any]:
    """
    Entry point chính của AI Engine để Backend FastAPI gọi tới.
    """
    diff_key = difficulty.upper()
    config = DIFFICULTY_CONFIG.get(diff_key, DIFFICULTY_CONFIG["MEDIUM"])

    start_time = time.perf_counter()

    (row, col), score = find_best_move(
        board=board,
        ai_player=ai_player,
        depth=config["depth"],
        candidate_limit=config["candidate_limit"]
    )

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return {
        "row": row,
        "col": col,
        "score": score,
        "elapsed_ms": round(elapsed_ms, 2)
    }

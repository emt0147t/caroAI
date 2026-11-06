"""Narrowly scoped endpoints for controlled production acceptance runs."""

from fastapi import APIRouter, Depends, Header, HTTPException

from app.api.dependencies import get_game_service
from app.db.repository import GamePersistenceError
from app.domain.game_state import GameMode
from app.schemas.game import GameCreateRequest, GameResponse
from app.services.game_service import GameService


router = APIRouter(prefix="/api/qa", tags=["production-qa"])


def _qa_run_id(
    run_id: str = Header(
        ...,
        alias="X-CaroAI-QA-Run-ID",
        min_length=32,
        max_length=32,
        pattern="^[0-9a-f]{32}$",
    ),
) -> str:
    """Require a single run-scoped 128-bit hex capability."""
    return run_id


@router.post("/games", response_model=GameResponse, status_code=201)
def create_qa_game(
    request: GameCreateRequest,
    run_id: str = Depends(_qa_run_id),
    service: GameService = Depends(get_game_service),
):
    """Create a normal authoritative game tagged for exact-run cleanup."""
    try:
        game_id, state = service.create_game_with_state(
            request.mode, qa_run_id=run_id
        )
    except GamePersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Game storage is temporarily unavailable."
        ) from exc
    return GameResponse(
        id=game_id,
        mode=state.mode,
        status=state.status,
        current_player=state.current_player,
        move_count=state.move_count,
        winner=state.winner,
        board=state.board,
    )


@router.delete("/runs")
def cleanup_qa_run(
    run_id: str = Depends(_qa_run_id),
    service: GameService = Depends(get_game_service),
):
    """Delete only the QA games created with the exact supplied run capability."""
    try:
        deleted_ids = service.delete_qa_run(run_id)
    except GamePersistenceError as exc:
        raise HTTPException(
            status_code=503, detail="Game storage is temporarily unavailable."
        ) from exc
    return {
        "deleted_count": len(deleted_ids),
        "deleted_game_ids": deleted_ids,
    }

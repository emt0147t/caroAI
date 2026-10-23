"""Game History API backed by the configured game repository."""

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_game_service
from app.db.repository import GamePersistenceError
from app.schemas.game import GameHistoryItem, GameHistoryResponse
from app.services.game_service import GameService


router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("", response_model=GameHistoryResponse)
def list_history(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: GameService = Depends(get_game_service),
):
    """List newest games first; fetch the board through the game detail route."""
    try:
        records = service.list_history(limit=limit, offset=offset)
    except GamePersistenceError as exc:
        raise HTTPException(
            status_code=503,
            detail="Game storage is temporarily unavailable.",
        ) from exc

    items = [
        GameHistoryItem(
            id=record.public_id,
            mode=record.mode,
            status=record.status,
            result=record.result,
            started_at=record.started_at,
            ended_at=record.ended_at,
            move_count=record.move_count,
        )
        for record in records
    ]
    return GameHistoryResponse(items=items, limit=limit, offset=offset)

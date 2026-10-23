from fastapi import APIRouter, Query

from app.api.routes_games import game_service


router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    return {"items": game_service.list_history(limit=limit, offset=offset)}

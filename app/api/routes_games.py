from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_game_service
from app.db.repository import GamePersistenceError
from app.domain.game_rules import InvalidMoveError
from app.schemas.game import (
    AIMoveRequest,
    GameCreateRequest,
    GameResponse,
    MakeMoveResponse,
    MoveResponse,
    MoveRequest,
)
from app.services.game_service import (
    GameNotFoundError,
    GameService,
    InvalidAIMoveError,
)


router = APIRouter(prefix="/api/games", tags=["games"])


def _to_game_response(game_id: str, state) -> GameResponse:
    return GameResponse(
        id=game_id,
        mode=state.mode,
        status=state.status,
        current_player=state.current_player,
        move_count=state.move_count,
        winner=state.winner,
        board=state.board,
    )


def _storage_unavailable(exc: GamePersistenceError) -> HTTPException:
    return HTTPException(
        status_code=503,
        detail="Game storage is temporarily unavailable.",
    )


@router.post("", response_model=GameResponse, status_code=201)
def create_game(
    request: GameCreateRequest,
    service: GameService = Depends(get_game_service),
):
    try:
        game_id, state = service.create_game_with_state(request.mode)
    except GamePersistenceError as exc:
        raise _storage_unavailable(exc) from exc

    return _to_game_response(game_id, state)


@router.get("/{game_id}", response_model=GameResponse)
def get_game(
    game_id: str,
    service: GameService = Depends(get_game_service),
):
    try:
        state = service.get_game(game_id)
    except GameNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except GamePersistenceError as exc:
        raise _storage_unavailable(exc) from exc

    return _to_game_response(game_id, state)


@router.post(
    "/{game_id}/moves",
    response_model=MakeMoveResponse,
)
def make_move(
    game_id: str,
    request: MoveRequest,
    service: GameService = Depends(get_game_service),
):
    try:
        move, state = service.make_move_with_state(game_id, request.row, request.col)
    except GameNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidMoveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GamePersistenceError as exc:
        raise _storage_unavailable(exc) from exc

    return MakeMoveResponse(
        move=MoveResponse(
            row=move.row,
            col=move.col,
            player=move.player,
            move_number=move.move_number,
        ),
        game=_to_game_response(game_id, state),
    )


@router.post(
    "/{game_id}/ai-move",
    response_model=MakeMoveResponse,
)
def make_ai_move(
    game_id: str,
    request: AIMoveRequest,
    service: GameService = Depends(get_game_service),
):
    try:
        move, state = service.make_ai_move_with_state(
            game_id, request.difficulty.value
        )
    except GameNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidAIMoveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except GamePersistenceError as exc:
        raise _storage_unavailable(exc) from exc

    return MakeMoveResponse(
        move=MoveResponse(
            row=move.row,
            col=move.col,
            player=move.player,
            move_number=move.move_number,
        ),
        game=_to_game_response(game_id, state),
    )

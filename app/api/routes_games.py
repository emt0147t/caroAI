from fastapi import APIRouter, HTTPException

from app.domain.game_rules import InvalidMoveError
from app.schemas.game import (
    AIDifficulty,
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

game_service = GameService()


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


@router.post("", response_model=GameResponse, status_code=201)
def create_game(request: GameCreateRequest):
    game_id = game_service.create_game(request.mode)
    state = game_service.get_game(game_id)

    return _to_game_response(game_id, state)


@router.get("/{game_id}", response_model=GameResponse)
def get_game(game_id: str):
    try:
        state = game_service.get_game(game_id)
    except GameNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return _to_game_response(game_id, state)


@router.post(
    "/{game_id}/moves",
    response_model=MakeMoveResponse,
)
def make_move(game_id: str, request: MoveRequest):
    try:
        move = game_service.make_move(
            game_id,
            request.row,
            request.col,
        )
        state = game_service.get_game(game_id)

    except GameNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except InvalidMoveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

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
def make_ai_move(game_id: str, request: AIMoveRequest):
    try:
        move = game_service.make_ai_move(
            game_id,
            request.difficulty.value,
        )
        state = game_service.get_game(game_id)

    except GameNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    except InvalidAIMoveError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return MakeMoveResponse(
        move=MoveResponse(
            row=move.row,
            col=move.col,
            player=move.player,
            move_number=move.move_number,
        ),
        game=_to_game_response(game_id, state),
    )

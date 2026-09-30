from pydantic import BaseModel, Field

from app.domain.game_state import GameMode, GameStatus, Player


class GameCreateRequest(BaseModel):
    mode: GameMode = GameMode.HUMAN_VS_HUMAN


class MoveRequest(BaseModel):
    row: int = Field(ge=0, le=14)
    col: int = Field(ge=0, le=14)


class MoveResponse(BaseModel):
    row: int
    col: int
    player: Player
    move_number: int


class GameResponse(BaseModel):
    id: str
    mode: GameMode
    status: GameStatus
    current_player: Player
    move_count: int
    winner: Player | None
    board: list[list[str]]


class MakeMoveResponse(BaseModel):
    move: MoveResponse
    game: GameResponse
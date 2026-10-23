from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field

from app.domain.game_state import GameMode, GameStatus, Player


class GameCreateRequest(BaseModel):
    mode: GameMode = GameMode.HUMAN_VS_HUMAN


class MoveRequest(BaseModel):
    row: int = Field(ge=0, le=14)
    col: int = Field(ge=0, le=14)


class AIDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class AIMoveRequest(BaseModel):
    difficulty: AIDifficulty = AIDifficulty.MEDIUM


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


class GameHistoryItem(BaseModel):
    """Metadata for one persisted game in the history list."""

    id: str
    mode: GameMode
    status: GameStatus
    result: GameStatus | None
    started_at: datetime
    ended_at: datetime | None
    move_count: int


class GameHistoryResponse(BaseModel):
    """Paginated Game History API response."""

    items: list[GameHistoryItem]
    limit: int
    offset: int

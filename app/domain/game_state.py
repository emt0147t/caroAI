from dataclasses import dataclass, field
from enum import Enum


BOARD_SIZE = 15


class Player(str, Enum):
    X = "X"
    O = "O"


class GameMode(str, Enum):
    HUMAN_VS_HUMAN = "HUMAN_VS_HUMAN"
    HUMAN_VS_AI = "HUMAN_VS_AI"


class GameStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    X_WON = "X_WON"
    O_WON = "O_WON"
    DRAW = "DRAW"


@dataclass(frozen=True)
class Move:
    row: int
    col: int
    player: Player
    move_number: int


@dataclass
class GameState:
    board: list[list[str]] = field(
        default_factory=lambda: [
            ["EMPTY" for _ in range(BOARD_SIZE)]
            for _ in range(BOARD_SIZE)
        ]
    )
    current_player: Player = Player.X
    mode: GameMode = GameMode.HUMAN_VS_HUMAN
    status: GameStatus = GameStatus.IN_PROGRESS
    move_count: int = 0
    winner: Player | None = None
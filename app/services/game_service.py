from uuid import uuid4

from app.domain.game_rules import GameRules
from app.domain.game_state import GameMode, GameState


class GameNotFoundError(ValueError):
    """Raised when a requested game does not exist."""


class GameService:
    """
    Application service for managing Caro games.

    Sprint 1 uses in-memory storage.
    PostgreSQL persistence will be introduced later.
    """

    def __init__(self) -> None:
        self._games: dict[str, GameState] = {}

    def create_game(self, mode: GameMode) -> str:
        game_id = str(uuid4())
        self._games[game_id] = GameState(mode=mode)
        return game_id

    def get_game(self, game_id: str) -> GameState:
        state = self._games.get(game_id)

        if state is None:
            raise GameNotFoundError(f"Game '{game_id}' not found")

        return state

    def make_move(self, game_id: str, row: int, col: int):
        state = self.get_game(game_id)

        return GameRules.apply_move(
            state,
            row,
            col,
        )
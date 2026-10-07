from uuid import uuid4

from app.ai.adapter import board_to_ai
from app.ai.engine import get_ai_move as run_ai_engine
from app.domain.game_rules import GameRules, InvalidMoveError
from app.domain.game_state import GameMode, GameState, Player


class GameNotFoundError(ValueError):
    """Raised when a requested game does not exist."""


class InvalidAIMoveError(ValueError):
    """Raised when the AI cannot provide a legal move for the current game."""


class GameService:
    """Application service for managing Caro games."""

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

    def make_ai_move(self, game_id: str, difficulty: str):
        """Request an AI decision and apply it through the authoritative game rules."""
        state = self.get_game(game_id)

        if state.mode != GameMode.HUMAN_VS_AI:
            raise InvalidAIMoveError(
                "AI move is only available for HUMAN_VS_AI games"
            )

        if state.current_player != Player.O:
            raise InvalidAIMoveError("It is not the AI turn")

        # Convert to a fresh snapshot so AI search can never mutate Backend state.
        ai_board = board_to_ai(state.board)
        result = run_ai_engine(
            board=ai_board,
            ai_player=2,
            difficulty=difficulty,
        )

        row = result.get("row")
        col = result.get("col")
        if not isinstance(row, int) or not isinstance(col, int):
            raise InvalidAIMoveError("AI returned an invalid move")

        try:
            GameRules.validate_move(state, row, col)
        except InvalidMoveError as exc:
            raise InvalidAIMoveError(
                f"AI returned an illegal move: {exc}"
            ) from exc

        # Only Backend GameRules may mutate GameState and determine game status.
        return GameRules.apply_move(state, row, col)

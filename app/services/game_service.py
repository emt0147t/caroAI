from datetime import datetime, timezone
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

    VALID_AI_DIFFICULTIES = frozenset({"easy", "medium", "hard"})

    def __init__(self) -> None:
        self._games: dict[str, GameState] = {}
        self._created_at: dict[str, datetime] = {}

    def create_game(self, mode: GameMode) -> str:
        game_id = str(uuid4())
        self._games[game_id] = GameState(mode=mode)
        self._created_at[game_id] = datetime.now(timezone.utc)
        return game_id

    def list_history(self, limit: int, offset: int) -> list[dict[str, str | int | None]]:
        ordered_ids = sorted(
            self._games.keys(),
            key=lambda game_id: self._created_at.get(game_id, datetime.min.replace(tzinfo=timezone.utc)),
            reverse=True,
        )
        page_ids = ordered_ids[offset : offset + limit]
        items: list[dict[str, str | int | None]] = []
        for game_id in page_ids:
            state = self._games[game_id]
            started_at = self._created_at.get(game_id)
            items.append(
                {
                    "id": game_id,
                    "mode": state.mode.value,
                    "status": state.status.value,
                    "result": state.status.value if state.status.value != "IN_PROGRESS" else None,
                    "move_count": state.move_count,
                    "started_at": started_at.isoformat() if started_at else None,
                }
            )
        return items

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

        if difficulty not in self.VALID_AI_DIFFICULTIES:
            raise InvalidAIMoveError(
                "Difficulty must be one of: easy, medium, hard"
            )

        # Convert to a fresh snapshot so AI search can never mutate Backend state.
        ai_board = board_to_ai(state.board)
        result = run_ai_engine(
            board=ai_board,
            ai_player=2,
            difficulty=difficulty,
        )

        if not isinstance(result, dict):
            raise InvalidAIMoveError("AI returned an invalid move response")

        row = result.get("row")
        col = result.get("col")
        if not isinstance(row, int) or isinstance(row, bool):
            raise InvalidAIMoveError("AI returned an invalid row")
        if not isinstance(col, int) or isinstance(col, bool):
            raise InvalidAIMoveError("AI returned an invalid column")

        try:
            GameRules.validate_move(state, row, col)
        except InvalidMoveError as exc:
            raise InvalidAIMoveError(
                f"AI returned an illegal move: {exc}"
            ) from exc

        # Only Backend GameRules may mutate GameState and determine game status.
        return GameRules.apply_move(state, row, col)

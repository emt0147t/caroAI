"""Application service for authoritative Caro game behavior."""
from app.ai.adapter import board_to_ai
from app.ai.engine import get_ai_move as run_ai_engine
from app.db.repository import (
    GamePersistenceError,
    InMemoryGameRepository,
    RepositoryGameNotFoundError,
)
from app.domain.game_rules import GameRules, InvalidMoveError
from app.domain.game_state import GameMode, GameState, Move, Player


class GameNotFoundError(ValueError):
    """Raised when a requested game does not exist."""


class InvalidAIMoveError(ValueError):
    """Raised when the AI cannot provide a legal move for the current game."""


class GameService:
    """Application service; storage is injected so production uses PostgreSQL."""

    VALID_AI_DIFFICULTIES = frozenset({"easy", "medium", "hard"})

    def __init__(self, repository=None) -> None:
        # Keep construction without arguments useful for legacy unit tests, but
        # production routes always inject SQLAlchemyGameRepository explicitly.
        self._repository = repository or InMemoryGameRepository()

    def create_game(self, mode: GameMode) -> str:
        with self._repository.transaction() as uow:
            return uow.create_game(mode)

    def get_game(self, game_id: str) -> GameState:
        try:
            with self._repository.transaction() as uow:
                return uow.get_game_state(game_id)
        except RepositoryGameNotFoundError as exc:
            raise GameNotFoundError(str(exc)) from exc

    def make_move(self, game_id: str, row: int, col: int) -> Move:
        try:
            with self._repository.transaction() as uow:
                state = uow.get_game_state(game_id, for_update=True)
                move = GameRules.apply_move(state, row, col)
                uow.persist_move(game_id, move, state)
                return move
        except RepositoryGameNotFoundError as exc:
            raise GameNotFoundError(str(exc)) from exc

    def make_ai_move(self, game_id: str, difficulty: str) -> Move:
        """Compute, validate and persist an AI move in one transaction."""
        try:
            with self._repository.transaction() as uow:
                state = uow.get_game_state(game_id, for_update=True)

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

                # AI receives a fresh snapshot and cannot mutate Backend state.
                result = run_ai_engine(
                    board=board_to_ai(state.board),
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
                    move = GameRules.apply_move(state, row, col)
                except InvalidMoveError as exc:
                    raise InvalidAIMoveError(
                        f"AI returned an illegal move: {exc}"
                    ) from exc

                uow.persist_move(game_id, move, state)
                return move
        except RepositoryGameNotFoundError as exc:
            raise GameNotFoundError(str(exc)) from exc

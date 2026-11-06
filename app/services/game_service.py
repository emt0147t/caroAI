"""Application service for authoritative Caro game behavior."""
from copy import deepcopy

from app.ai.adapter import board_to_ai
from app.observability import record_ai_admission_rejection, record_ai_search
from app.ai.admission import (
    AIAdmissionRejectedError,
    ImpossibleAdmissionGuard,
    get_default_impossible_admission_guard,
)
from app.ai.engine import get_ai_move as run_ai_engine
from app.db.repository import (
    InMemoryGameRepository,
    RepositoryGameNotFoundError,
)
from app.domain.game_rules import GameRules, InvalidMoveError
from app.domain.game_state import GameMode, GameState, Move, Player


class GameNotFoundError(ValueError):
    """Raised when a requested game does not exist."""


class InvalidAIMoveError(ValueError):
    """Raised when the AI cannot provide a legal move for the current game."""


class GameStateChangedError(RuntimeError):
    """Raised when the board changes while an AI move is being calculated."""


class GameService:
    """Application service; storage is injected so production uses PostgreSQL."""

    VALID_AI_DIFFICULTIES = frozenset({"easy", "medium", "hard", "impossible"})

    def __init__(
        self, repository=None, *, impossible_guard: ImpossibleAdmissionGuard | None = None
    ) -> None:
        # Keep construction without arguments useful for legacy unit tests, but
        # production routes always inject SQLAlchemyGameRepository explicitly.
        self._repository = repository or InMemoryGameRepository()
        self._impossible_guard = (
            impossible_guard or get_default_impossible_admission_guard()
        )

    def create_game_with_state(
        self, mode: GameMode, *, qa_run_id: str | None = None
    ) -> tuple[str, GameState]:
        """Create a game; QA tagging is only accepted by the dedicated QA route."""
        with self._repository.transaction() as uow:
            game_id = uow.create_game(mode, qa_run_id=qa_run_id)
            state = uow.get_game_state(game_id)
            return game_id, state

    def create_game(
        self, mode: GameMode, *, qa_run_id: str | None = None
    ) -> str:
        """Create a game and return its public identifier."""
        game_id, _state = self.create_game_with_state(mode, qa_run_id=qa_run_id)
        return game_id

    def delete_qa_run(self, qa_run_id: str) -> list[str]:
        """Delete only games explicitly tagged by one production QA run."""
        with self._repository.transaction() as uow:
            return uow.delete_qa_games(qa_run_id)

    def get_game(self, game_id: str) -> GameState:
        try:
            with self._repository.transaction() as uow:
                return uow.get_game_state(game_id)
        except RepositoryGameNotFoundError as exc:
            raise GameNotFoundError(str(exc)) from exc

    def make_move_with_state(
        self, game_id: str, row: int, col: int
    ) -> tuple[Move, GameState]:
        """Persist a move and return the resulting state before leaving the UoW."""
        try:
            with self._repository.transaction() as uow:
                state = uow.get_game_state(game_id, for_update=True)
                move = GameRules.apply_move(state, row, col)
                uow.persist_move(game_id, move, state)
                return move, state
        except RepositoryGameNotFoundError as exc:
            raise GameNotFoundError(str(exc)) from exc

    def make_move(self, game_id: str, row: int, col: int) -> Move:
        move, _state = self.make_move_with_state(game_id, row, col)
        return move

    def list_history(self, *, limit: int = 50, offset: int = 0):
        """Return paginated game summaries from the configured repository."""
        with self._repository.transaction() as uow:
            return uow.list_history(limit=limit, offset=offset)

    def _choose_ai_coordinates(
        self, state: GameState, difficulty: str
    ) -> tuple[int, int]:
        if state.mode != GameMode.HUMAN_VS_AI:
            raise InvalidAIMoveError(
                "AI move is only available for HUMAN_VS_AI games"
            )
        if state.current_player != Player.O:
            raise InvalidAIMoveError("It is not the AI turn")
        if difficulty not in self.VALID_AI_DIFFICULTIES:
            raise InvalidAIMoveError(
                "Difficulty must be one of: easy, medium, hard, impossible"
            )

        result = run_ai_engine(
            board=board_to_ai(state.board),
            ai_player=2,
            difficulty=difficulty,
        )
        if not isinstance(result, dict):
            raise InvalidAIMoveError("AI returned an invalid move response")
        record_ai_search(difficulty, result)

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
        return row, col

    def make_ai_move_with_state(
        self, game_id: str, difficulty: str
    ) -> tuple[Move, GameState]:
        """Search outside the write lock, then revalidate and atomically persist."""
        try:
            if difficulty == "impossible":
                try:
                    with self._impossible_guard.acquire():
                        return self._make_ai_move_with_snapshot(game_id, difficulty)
                except AIAdmissionRejectedError:
                    record_ai_admission_rejection()
                    raise
            return self._make_ai_move_with_snapshot(game_id, difficulty)
        except RepositoryGameNotFoundError as exc:
            raise GameNotFoundError(str(exc)) from exc

    def _make_ai_move_with_snapshot(
        self, game_id: str, difficulty: str
    ) -> tuple[Move, GameState]:
        # Read a coherent state snapshot and release the transaction/connection
        # before invoking Minimax. The engine receives a detached domain object.
        with self._repository.transaction() as uow:
            snapshot = deepcopy(uow.get_game_state(game_id))
        row, col = self._choose_ai_coordinates(snapshot, difficulty)

        # Re-read under the parent-row lock. A human or competing AI request may
        # have committed while search was running; never persist a stale move.
        with self._repository.transaction() as uow:
            current = uow.get_game_state(game_id, for_update=True)
            if current != snapshot:
                raise GameStateChangedError(
                    "Game state changed while the AI was searching; reload the game"
                )
            move = GameRules.apply_move(current, row, col)
            uow.persist_move(game_id, move, current)
            return move, current

    def make_ai_move(self, game_id: str, difficulty: str) -> Move:
        move, _state = self.make_ai_move_with_state(game_id, difficulty)
        return move

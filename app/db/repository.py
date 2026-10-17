"""Repository and transaction unit-of-work for CaroAI game state."""
from contextlib import contextmanager
from copy import deepcopy
from threading import RLock
from typing import Iterator
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import Game as GameRecord
from app.db.models import Move as PersistedMove
from app.domain.game_rules import GameRules, InvalidMoveError
from app.domain.game_state import GameMode, GameState, GameStatus, Move


class RepositoryGameNotFoundError(LookupError):
    """Raised when a public game ID does not identify a persisted game."""


class GamePersistenceError(RuntimeError):
    """Raised when a persisted game cannot be read or written consistently."""


def _result_for_state(state: GameState) -> str | None:
    """Persist terminal outcomes using the same values as GameStatus."""
    if state.status == GameStatus.IN_PROGRESS:
        return None
    return state.status.value


def _rebuild_state(record: GameRecord, moves: list[PersistedMove]) -> GameState:
    """Rebuild the authoritative domain state from ordered persisted moves."""
    try:
        state = GameState(mode=GameMode(record.mode))
    except ValueError as exc:
        raise GamePersistenceError("Stored game has an unsupported mode.") from exc

    for expected_number, persisted_move in enumerate(moves, start=1):
        if persisted_move.move_number != expected_number:
            raise GamePersistenceError("Stored move numbers are not contiguous.")
        if persisted_move.player != state.current_player.value:
            raise GamePersistenceError("Stored move order does not match player turns.")

        try:
            applied = GameRules.apply_move(
                state, persisted_move.row, persisted_move.col
            )
        except InvalidMoveError as exc:
            raise GamePersistenceError(
                "Stored move history violates the game rules."
            ) from exc

        if applied.move_number != persisted_move.move_number:
            raise GamePersistenceError("Stored move number does not match history.")

    expected_result = _result_for_state(state)
    if record.status != state.status.value or record.result != expected_result:
        raise GamePersistenceError(
            "Stored game status/result is inconsistent with its move history."
        )

    return state


class SQLAlchemyGameUnitOfWork:
    """Database operations within one SQLAlchemy transaction."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self._loaded_records: dict[str, GameRecord] = {}

    def create_game(self, mode: GameMode) -> str:
        public_id = str(uuid4())
        record = GameRecord(
            public_id=public_id,
            mode=mode.value,
            status=GameStatus.IN_PROGRESS.value,
            result=None,
        )
        self.session.add(record)
        self.session.flush()
        self._loaded_records[public_id] = record
        return public_id

    def get_game_state(
        self, game_id: str, *, for_update: bool = False
    ) -> GameState:
        statement = select(GameRecord).where(GameRecord.public_id == game_id)
        if for_update:
            statement = statement.with_for_update()

        record = self.session.execute(statement).scalar_one_or_none()
        if record is None:
            raise RepositoryGameNotFoundError(f"Game '{game_id}' not found")

        self._loaded_records[game_id] = record
        moves = self.session.scalars(
            select(PersistedMove)
            .where(PersistedMove.game_id == record.id)
            .order_by(PersistedMove.move_number.asc())
        ).all()
        return _rebuild_state(record, list(moves))

    def persist_move(self, game_id: str, move: Move, state: GameState) -> None:
        record = self._loaded_records.get(game_id)
        if record is None:
            raise GamePersistenceError(
                "A game must be loaded inside the transaction before writing a move."
            )

        self.session.add(
            PersistedMove(
                game_id=record.id,
                player=move.player.value,
                row=move.row,
                col=move.col,
                move_number=move.move_number,
            )
        )
        record.status = state.status.value
        record.result = _result_for_state(state)
        record.ended_at = (
            func.now() if state.status != GameStatus.IN_PROGRESS else None
        )
        self.session.flush()


class SQLAlchemyGameRepository:
    """SQLAlchemy-backed repository; the caller owns the request-scoped Session."""

    def __init__(self, session: Session) -> None:
        self.session = session

    @contextmanager
    def transaction(self) -> Iterator[SQLAlchemyGameUnitOfWork]:
        try:
            with self.session.begin():
                yield SQLAlchemyGameUnitOfWork(self.session)
        except SQLAlchemyError as exc:
            raise GamePersistenceError(
                "Game storage is temporarily unavailable."
            ) from exc


class InMemoryGameUnitOfWork:
    """Small transactional adapter for isolated unit/API tests only."""

    def __init__(self, games: dict[str, GameState]) -> None:
        self._games = games

    def create_game(self, mode: GameMode) -> str:
        game_id = str(uuid4())
        self._games[game_id] = GameState(mode=mode)
        return game_id

    def get_game_state(
        self, game_id: str, *, for_update: bool = False
    ) -> GameState:
        state = self._games.get(game_id)
        if state is None:
            raise RepositoryGameNotFoundError(f"Game '{game_id}' not found")
        return state

    def persist_move(self, game_id: str, move: Move, state: GameState) -> None:
        if game_id not in self._games:
            raise RepositoryGameNotFoundError(f"Game '{game_id}' not found")
        self._games[game_id] = deepcopy(state)


class InMemoryGameRepository:
    """In-memory repository that must not be used by the production API."""

    def __init__(self) -> None:
        self._games: dict[str, GameState] = {}
        self._lock = RLock()

    @contextmanager
    def transaction(self) -> Iterator[InMemoryGameUnitOfWork]:
        with self._lock:
            working_copy = deepcopy(self._games)
            try:
                yield InMemoryGameUnitOfWork(working_copy)
            except Exception:
                raise
            else:
                self._games = working_copy

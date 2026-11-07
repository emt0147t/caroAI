"""Repository and transaction unit-of-work for CaroAI game state."""
from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from threading import RLock
from typing import Iterator
from uuid import uuid4

from sqlalchemy import case, delete, func, select
from sqlalchemy.dialects.postgresql import insert as postgres_insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db.models import Game as GameRecord
from app.db.models import GameAnalysis
from app.db.models import Move as PersistedMove
from app.db.models import QARunUsage
from app.domain.game_rules import GameRules, InvalidMoveError
from app.domain.game_state import GameMode, GameState, GameStatus, Move


class RepositoryGameNotFoundError(LookupError):
    """Raised when a public game ID does not identify a persisted game."""


class GamePersistenceError(RuntimeError):
    """Raised when a persisted game cannot be read or written consistently."""


class QARunLimitExceededError(RuntimeError):
    """Raised when a QA run has consumed its deployment-wide game quota."""


@dataclass(frozen=True)
class GameHistoryRecord:
    """Storage-neutral summary for the Game History API."""

    public_id: str
    mode: str
    status: str
    result: str | None
    started_at: datetime
    ended_at: datetime | None
    move_count: int


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

    def create_game(
        self,
        mode: GameMode,
        *,
        qa_run_id: str | None = None,
        qa_max_games: int | None = None,
        qa_expires_at: int | None = None,
    ) -> str:
        if qa_run_id is not None and qa_max_games is not None:
            if qa_expires_at is None:
                raise ValueError("QA quota requires the capability expiry")
            if self.session.bind.dialect.name != "postgresql":
                raise RuntimeError("QA creation quota requires PostgreSQL")
            now = int(datetime.now(timezone.utc).timestamp())
            self.session.execute(
                delete(QARunUsage).where(QARunUsage.expires_at <= now)
            )
            quota = (
                postgres_insert(QARunUsage)
                .values(
                    qa_run_id=qa_run_id,
                    games_created=1,
                    expires_at=qa_expires_at,
                )
                .on_conflict_do_update(
                    index_elements=[QARunUsage.qa_run_id],
                    set_={
                        "games_created": case(
                            (QARunUsage.expires_at <= now, 1),
                            else_=QARunUsage.games_created + 1,
                        ),
                        "expires_at": func.greatest(
                            QARunUsage.expires_at, qa_expires_at
                        ),
                    },
                    where=(
                        (QARunUsage.expires_at <= now)
                        | (QARunUsage.games_created < qa_max_games)
                    ),
                )
                .returning(QARunUsage.games_created)
            )
            if self.session.execute(quota).scalar_one_or_none() is None:
                raise QARunLimitExceededError(
                    "This QA run has reached its game creation limit."
                )

        public_id = str(uuid4())
        record = GameRecord(
            public_id=public_id,
            mode=mode.value,
            status=GameStatus.IN_PROGRESS.value,
            result=None,
            qa_run_id=qa_run_id,
        )
        self.session.add(record)
        self.session.flush()
        self._loaded_records[public_id] = record
        return public_id

    def get_game_state(
        self, game_id: str, *, for_update: bool = False
    ) -> GameState:
        if for_update:
            # Writers lock the parent row before reading moves. Keep these as
            # separate queries: after a lock wait, the moves query must observe
            # the committed state of the row that was actually locked.
            statement = (
                select(GameRecord)
                .where(GameRecord.public_id == game_id)
                .with_for_update()
                .execution_options(populate_existing=True)
            )
            record = self.session.execute(statement).scalar_one_or_none()
            if record is None:
                raise RepositoryGameNotFoundError(
                    f"Game '{game_id}' not found"
                )

            self._loaded_records[game_id] = record
            moves = self.session.scalars(
                select(PersistedMove)
                .where(PersistedMove.game_id == record.id)
                .order_by(PersistedMove.move_number.asc())
            ).all()
            return _rebuild_state(record, list(moves))

        # A non-locking GET must read metadata and move history from the same
        # SQL statement snapshot. Two SELECTs under PostgreSQL READ COMMITTED
        # can otherwise straddle a concurrent move commit (old game status,
        # new move history) and report a false persistence inconsistency.
        statement = (
            select(GameRecord, PersistedMove)
            .outerjoin(
                PersistedMove,
                PersistedMove.game_id == GameRecord.id,
            )
            .where(GameRecord.public_id == game_id)
            .order_by(PersistedMove.move_number.asc())
            .execution_options(populate_existing=True)
        )
        rows = self.session.execute(statement).all()
        if not rows:
            raise RepositoryGameNotFoundError(f"Game '{game_id}' not found")

        record = rows[0][0]
        moves = [
            persisted_move
            for _record, persisted_move in rows
            if persisted_move is not None
        ]
        self._loaded_records[game_id] = record
        return _rebuild_state(record, moves)

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

    def delete_qa_games(self, qa_run_id: str) -> list[str]:
        """Delete only games explicitly tagged with the exact QA run capability."""
        records = self.session.scalars(
            select(GameRecord).where(GameRecord.qa_run_id == qa_run_id)
        ).all()
        if not records:
            return []
        internal_ids = [record.id for record in records]
        public_ids = [record.public_id for record in records]

        # game_analysis.move_id references moves, so analysis rows are removed
        # before moves and parent games in the same transaction.
        self.session.execute(
            delete(GameAnalysis).where(GameAnalysis.game_id.in_(internal_ids))
        )
        self.session.execute(
            delete(PersistedMove).where(PersistedMove.game_id.in_(internal_ids))
        )
        self.session.execute(
            delete(GameRecord).where(GameRecord.id.in_(internal_ids))
        )
        return public_ids

    def list_history(
        self, *, limit: int = 50, offset: int = 0
    ) -> list[GameHistoryRecord]:
        """Return newest games first with persisted move counts."""
        move_count = (
            select(func.count(PersistedMove.id))
            .where(PersistedMove.game_id == GameRecord.id)
            .correlate(GameRecord)
            .scalar_subquery()
        )
        statement = (
            select(GameRecord, move_count.label("move_count"))
            .order_by(GameRecord.started_at.desc(), GameRecord.id.desc())
            .offset(offset)
            .limit(limit)
        )
        rows = self.session.execute(statement).all()
        return [
            GameHistoryRecord(
                public_id=record.public_id,
                mode=record.mode,
                status=record.status,
                result=record.result,
                started_at=record.started_at,
                ended_at=record.ended_at,
                move_count=int(count),
            )
            for record, count in rows
        ]


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

    def __init__(
        self,
        games: dict[str, GameState],
        started_at: dict[str, datetime],
        ended_at: dict[str, datetime],
        qa_run_ids: dict[str, str],
        qa_run_usage: dict[str, tuple[int, int]],
    ) -> None:
        self._games = games
        self._started_at = started_at
        self._ended_at = ended_at
        self._qa_run_ids = qa_run_ids
        self._qa_run_usage = qa_run_usage

    def create_game(
        self,
        mode: GameMode,
        *,
        qa_run_id: str | None = None,
        qa_max_games: int | None = None,
        qa_expires_at: int | None = None,
    ) -> str:
        if qa_run_id is not None and qa_max_games is not None:
            if qa_expires_at is None:
                raise ValueError("QA quota requires the capability expiry")
            count, prior_expiry = self._qa_run_usage.get(qa_run_id, (0, 0))
            if prior_expiry <= int(datetime.now(timezone.utc).timestamp()):
                count = 0
            if count >= qa_max_games:
                raise QARunLimitExceededError(
                    "This QA run has reached its game creation limit."
                )
            self._qa_run_usage[qa_run_id] = (
                count + 1,
                max(prior_expiry, qa_expires_at),
            )
        game_id = str(uuid4())
        self._games[game_id] = GameState(mode=mode)
        self._started_at[game_id] = datetime.now(timezone.utc)
        if qa_run_id is not None:
            self._qa_run_ids[game_id] = qa_run_id
        return game_id

    def delete_qa_games(self, qa_run_id: str) -> list[str]:
        game_ids = [
            game_id for game_id, tagged_run in self._qa_run_ids.items()
            if tagged_run == qa_run_id
        ]
        for game_id in game_ids:
            self._games.pop(game_id, None)
            self._started_at.pop(game_id, None)
            self._ended_at.pop(game_id, None)
            self._qa_run_ids.pop(game_id, None)
        return game_ids

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
        if state.status == GameStatus.IN_PROGRESS:
            self._ended_at.pop(game_id, None)
        else:
            self._ended_at[game_id] = datetime.now(timezone.utc)

    def list_history(
        self, *, limit: int = 50, offset: int = 0
    ) -> list[GameHistoryRecord]:
        """Return recent in-memory games in the same shape as SQL persistence."""
        ordered_ids = sorted(
            self._games,
            key=lambda game_id: (self._started_at[game_id], game_id),
            reverse=True,
        )
        selected_ids = ordered_ids[offset:offset + limit]
        records = []
        for game_id in selected_ids:
            state = self._games[game_id]
            result = (
                None
                if state.status == GameStatus.IN_PROGRESS
                else state.status.value
            )
            records.append(
                GameHistoryRecord(
                    public_id=game_id,
                    mode=state.mode.value,
                    status=state.status.value,
                    result=result,
                    started_at=self._started_at[game_id],
                    ended_at=self._ended_at.get(game_id),
                    move_count=state.move_count,
                )
            )
        return records


class InMemoryGameRepository:
    """In-memory repository that must not be used by the production API."""

    def __init__(self) -> None:
        self._games: dict[str, GameState] = {}
        self._started_at: dict[str, datetime] = {}
        self._ended_at: dict[str, datetime] = {}
        self._qa_run_ids: dict[str, str] = {}
        self._qa_run_usage: dict[str, tuple[int, int]] = {}
        self._lock = RLock()

    @contextmanager
    def transaction(self) -> Iterator[InMemoryGameUnitOfWork]:
        with self._lock:
            working_copy = deepcopy(self._games)
            started_at_copy = deepcopy(self._started_at)
            ended_at_copy = deepcopy(self._ended_at)
            qa_run_ids_copy = deepcopy(self._qa_run_ids)
            qa_run_usage_copy = deepcopy(self._qa_run_usage)
            try:
                yield InMemoryGameUnitOfWork(
                    working_copy, started_at_copy, ended_at_copy,
                    qa_run_ids_copy,
                    qa_run_usage_copy,
                )
            except Exception:
                raise
            else:
                self._games = working_copy
                self._started_at = started_at_copy
                self._ended_at = ended_at_copy
                self._qa_run_ids = qa_run_ids_copy
                self._qa_run_usage = qa_run_usage_copy

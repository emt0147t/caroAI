"""Service/API persistence tests using SQLite as a portable SQLAlchemy target."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_game_service
from app.db.models import Base, Game, Move
from app.db.repository import SQLAlchemyGameRepository, SQLAlchemyGameUnitOfWork
from app.domain.game_state import GameMode, GameStatus, Player
from app.main import app
from app.services.game_service import GameService


@pytest.fixture
def database():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def enable_foreign_keys(connection, _record):
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(engine)
    session_factory = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    try:
        yield engine, session_factory
    finally:
        engine.dispose()


def test_service_persists_game_and_moves_across_sessions(database):
    _engine, session_factory = database
    with session_factory() as session:
        service = GameService(SQLAlchemyGameRepository(session))
        game_id = service.create_game(GameMode.HUMAN_VS_HUMAN)
        service.make_move(game_id, 7, 7)
        service.make_move(game_id, 7, 8)

    # A new SQLAlchemy Session proves that the repository reloads persisted data.
    with session_factory() as session:
        state = GameService(SQLAlchemyGameRepository(session)).get_game(game_id)
        assert state.mode == GameMode.HUMAN_VS_HUMAN
        assert state.board[7][7] == "X"
        assert state.board[7][8] == "O"
        assert state.move_count == 2
        assert state.current_player == Player.X
        assert state.status == GameStatus.IN_PROGRESS

        record = session.query(Game).filter_by(public_id=game_id).one()
        moves = session.scalars(
            select(Move)
            .where(Move.game_id == record.id)
            .order_by(Move.move_number.asc())
        ).all()
        assert [move.move_number for move in moves] == [1, 2]
        assert [move.player for move in moves] == ["X", "O"]


def test_api_reads_game_created_and_moved_in_previous_requests(database):
    _engine, session_factory = database

    def sql_game_service():
        with session_factory() as session:
            yield GameService(SQLAlchemyGameRepository(session))

    app.dependency_overrides[get_game_service] = sql_game_service
    try:
        with TestClient(app) as client:
            created = client.post(
                "/api/games",
                json={"mode": "HUMAN_VS_HUMAN"},
            )
            assert created.status_code == 201
            game_id = created.json()["id"]

            first_move = client.post(
                f"/api/games/{game_id}/moves",
                json={"row": 2, "col": 3},
            )
            assert first_move.status_code == 200
            assert first_move.json()["game"]["board"][2][3] == "X"

            second_move = client.post(
                f"/api/games/{game_id}/moves",
                json={"row": 2, "col": 4},
            )
            assert second_move.status_code == 200
            assert second_move.json()["game"]["board"][2][4] == "O"

            reloaded = client.get(f"/api/games/{game_id}")
            assert reloaded.status_code == 200
            assert reloaded.json()["id"] == game_id
            assert reloaded.json()["move_count"] == 2
            assert reloaded.json()["board"][2][3] == "X"
            assert reloaded.json()["board"][2][4] == "O"
    finally:
        app.dependency_overrides.pop(get_game_service, None)


def test_service_transaction_rolls_back_if_move_persistence_fails(database, monkeypatch):
    _engine, session_factory = database
    with session_factory() as session:
        service = GameService(SQLAlchemyGameRepository(session))
        game_id = service.create_game(GameMode.HUMAN_VS_HUMAN)

    original_persist_move = SQLAlchemyGameUnitOfWork.persist_move

    def fail_after_staging_move(self, target_game_id, move, state):
        original_persist_move(self, target_game_id, move, state)
        raise RuntimeError("simulated failure after staging the move")

    monkeypatch.setattr(
        SQLAlchemyGameUnitOfWork,
        "persist_move",
        fail_after_staging_move,
    )
    with session_factory() as session:
        service = GameService(SQLAlchemyGameRepository(session))
        with pytest.raises(RuntimeError, match="simulated failure"):
            service.make_move(game_id, 4, 5)

    with session_factory() as session:
        record = session.query(Game).filter_by(public_id=game_id).one()
        move_count = session.scalar(
            select(func.count()).select_from(Move).where(Move.game_id == record.id)
        )
        assert record.status == GameStatus.IN_PROGRESS.value
        assert record.result is None
        assert move_count == 0

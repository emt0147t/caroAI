"""Service/API persistence tests using SQLite as a portable SQLAlchemy target."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_game_service
from app.db.models import Base, Game, Move
from app.db.repository import (
    GamePersistenceError,
    SQLAlchemyGameRepository,
    SQLAlchemyGameUnitOfWork,
)
from app.domain.game_state import GameMode, GameStatus, Player
from app.main import app
from app.services import game_service as game_service_module
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


def test_terminal_result_and_end_time_persist_across_sessions(database):
    _engine, session_factory = database
    with session_factory() as session:
        service = GameService(SQLAlchemyGameRepository(session))
        game_id = service.create_game(GameMode.HUMAN_VS_HUMAN)
        # X makes a horizontal five; O replies elsewhere without making five.
        sequence = [
            (0, 0), (1, 0),
            (0, 1), (1, 1),
            (0, 2), (1, 2),
            (0, 3), (1, 3),
            (0, 4),
        ]
        for row, col in sequence:
            service.make_move(game_id, row, col)

    with session_factory() as session:
        state = GameService(SQLAlchemyGameRepository(session)).get_game(game_id)
        record = session.query(Game).filter_by(public_id=game_id).one()
        assert state.status == GameStatus.X_WON
        assert state.winner == Player.X
        assert state.move_count == 9
        assert record.status == GameStatus.X_WON.value
        assert record.result == GameStatus.X_WON.value
        assert record.ended_at is not None


def test_ai_move_is_persisted_and_read_back_across_sessions(database, monkeypatch):
    _engine, session_factory = database

    def fake_ai_move(board, ai_player, difficulty):
        assert ai_player == 2
        assert difficulty == "medium"
        assert board[7][7] == 1
        return {"row": 6, "col": 8}

    monkeypatch.setattr(game_service_module, "run_ai_engine", fake_ai_move)
    with session_factory() as session:
        service = GameService(SQLAlchemyGameRepository(session))
        game_id = service.create_game(GameMode.HUMAN_VS_AI)
        service.make_move(game_id, 7, 7)
        ai_move = service.make_ai_move(game_id, "medium")
        assert (ai_move.row, ai_move.col, ai_move.player.value) == (6, 8, "O")

    with session_factory() as session:
        state = GameService(SQLAlchemyGameRepository(session)).get_game(game_id)
        assert state.move_count == 2
        assert state.board[7][7] == "X"
        assert state.board[6][8] == "O"
        assert state.current_player == Player.X
        record = session.query(Game).filter_by(public_id=game_id).one()
        moves = session.scalars(
            select(Move)
            .where(Move.game_id == record.id)
            .order_by(Move.move_number.asc())
        ).all()
        assert [(move.player, move.move_number) for move in moves] == [("X", 1), ("O", 2)]


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


def test_history_api_returns_persisted_metadata_and_move_count(database):
    _engine, session_factory = database

    def sql_game_service():
        with session_factory() as session:
            yield GameService(SQLAlchemyGameRepository(session))

    app.dependency_overrides[get_game_service] = sql_game_service
    try:
        with TestClient(app) as client:
            created = client.post(
                "/api/games", json={"mode": "HUMAN_VS_HUMAN"}
            )
            assert created.status_code == 201
            game_id = created.json()["id"]
            moved = client.post(
                f"/api/games/{game_id}/moves",
                json={"row": 3, "col": 4},
            )
            assert moved.status_code == 200

            history = client.get("/api/history?limit=10&offset=0")
            assert history.status_code == 200
            payload = history.json()
            assert payload["limit"] == 10
            assert payload["offset"] == 0
            assert len(payload["items"]) == 1
            item = payload["items"][0]
            assert item["id"] == game_id
            assert item["mode"] == "HUMAN_VS_HUMAN"
            assert item["status"] == "IN_PROGRESS"
            assert item["result"] is None
            assert item["move_count"] == 1
            assert item["started_at"] is not None
            assert item["ended_at"] is None
            assert client.get("/api/history?limit=101").status_code == 422
    finally:
        app.dependency_overrides.pop(get_game_service, None)


def test_create_and_move_routes_do_not_read_state_after_write_commit(
    database, monkeypatch
):
    _engine, session_factory = database

    def sql_game_service():
        with session_factory() as session:
            yield GameService(SQLAlchemyGameRepository(session))

    def fail_if_called(_self, _game_id):
        raise GamePersistenceError("simulated follow-up read failure")

    monkeypatch.setattr(GameService, "get_game", fail_if_called)
    app.dependency_overrides[get_game_service] = sql_game_service
    try:
        with TestClient(app) as client:
            created = client.post(
                "/api/games", json={"mode": "HUMAN_VS_HUMAN"}
            )
            assert created.status_code == 201
            game_id = created.json()["id"]
            moved = client.post(
                f"/api/games/{game_id}/moves",
                json={"row": 5, "col": 6},
            )
            assert moved.status_code == 200
            assert moved.json()["game"]["move_count"] == 1
    finally:
        app.dependency_overrides.pop(get_game_service, None)

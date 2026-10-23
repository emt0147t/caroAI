"""Explicit PostgreSQL acceptance suite; invoke only in the dedicated CI job.

The non-test_ filename prevents the ordinary SQLite test job from collecting
this module. CI explicitly runs this file and fails if acceptance tests skip.
"""

import os
import re
from uuid import UUID, uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker

from app.api.dependencies import get_game_service
from app.db.models import Base, Game, Move
from app.db.repository import SQLAlchemyGameRepository, SQLAlchemyGameUnitOfWork
from app.domain.game_state import GameStatus
from app.main import app
from app.services import game_service as game_service_module
from app.services.game_service import GameService
from scripts.migrate_database import run_migrations


def _new_schema():
    """Create a unique schema only in a confirmed disposable test database."""
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        raise RuntimeError("TEST_DATABASE_URL is required for PostgreSQL acceptance")
    if os.getenv("CAROAI_TEST_DATABASE_CONFIRMED") != "disposable-test-database":
        raise RuntimeError("Disposable PostgreSQL confirmation is required")

    url = make_url(database_url)
    if url.get_backend_name() != "postgresql":
        raise RuntimeError("TEST_DATABASE_URL must use PostgreSQL")
    name = url.database or ""
    if not re.search(r"(^|[_-])test([_-]|$)", name, re.IGNORECASE):
        raise RuntimeError("Database name must visibly identify a test database")
    if re.search(r"prod(uction)?|live", name, re.IGNORECASE):
        raise RuntimeError("Refusing schema DDL against production/live database")

    schema = f"caroai_acceptance_{uuid4().hex}"
    admin_engine = create_engine(url, pool_pre_ping=True)
    engine = None
    try:
        with admin_engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        engine = create_engine(
            url,
            pool_pre_ping=True,
            connect_args={"options": f"-csearch_path={schema}"},
        )
        return admin_engine, engine, schema
    except Exception:
        admin_engine.dispose()
        if engine is not None:
            engine.dispose()
        raise


def _drop_schema(admin_engine, engine, schema):
    try:
        if engine is not None:
            engine.dispose()
        with admin_engine.begin() as connection:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
    finally:
        admin_engine.dispose()


def _override_game_service(engine):
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def sql_game_service():
        with factory() as session:
            yield GameService(SQLAlchemyGameRepository(session))

    app.dependency_overrides[get_game_service] = sql_game_service
    return factory


def test_postgres_api_human_ai_terminal_state_and_history(monkeypatch):
    admin_engine, engine, schema = _new_schema()
    try:
        Base.metadata.create_all(engine)
        factory = _override_game_service(engine)

        def fake_ai_move(board, ai_player, difficulty):
            assert ai_player == 2
            assert difficulty == "medium"
            assert board[7][7] == 1
            return {"row": 6, "col": 8}

        monkeypatch.setattr(game_service_module, "run_ai_engine", fake_ai_move)
        with TestClient(app) as client:
            response = client.post(
                "/api/games", json={"mode": "HUMAN_VS_HUMAN"}
            )
            assert response.status_code == 201
            game_id = response.json()["id"]
            moves = [
                (0, 0), (1, 0), (0, 1), (1, 1), (0, 2),
                (1, 2), (0, 3), (1, 3), (0, 4),
            ]
            for row, col in moves:
                response = client.post(
                    f"/api/games/{game_id}/moves",
                    json={"row": row, "col": col},
                )
                assert response.status_code == 200, response.text

            final_game = client.get(f"/api/games/{game_id}")
            assert final_game.status_code == 200
            assert final_game.json()["status"] == "X_WON"
            assert final_game.json()["winner"] == "X"
            assert final_game.json()["move_count"] == 9

            ai_created = client.post(
                "/api/games", json={"mode": "HUMAN_VS_AI"}
            )
            assert ai_created.status_code == 201
            ai_id = ai_created.json()["id"]
            human = client.post(
                f"/api/games/{ai_id}/moves", json={"row": 7, "col": 7}
            )
            assert human.status_code == 200
            ai = client.post(
                f"/api/games/{ai_id}/ai-move", json={"difficulty": "medium"}
            )
            assert ai.status_code == 200
            assert ai.json()["move"]["player"] == "O"
            assert ai.json()["game"]["board"][6][8] == "O"

            history = client.get("/api/history?limit=10&offset=0")
            assert history.status_code == 200
            by_id = {item["id"]: item for item in history.json()["items"]}
            assert set(by_id) == {game_id, ai_id}
            assert by_id[game_id]["status"] == "X_WON"
            assert by_id[game_id]["result"] == "X_WON"
            assert by_id[game_id]["move_count"] == 9
            assert by_id[game_id]["ended_at"] is not None
            assert by_id[ai_id]["move_count"] == 2

        with factory() as session:
            game = session.query(Game).filter_by(public_id=game_id).one()
            persisted_moves = session.scalars(
                select(Move)
                .where(Move.game_id == game.id)
                .order_by(Move.move_number)
            ).all()
            assert [move.move_number for move in persisted_moves] == list(range(1, 10))
            assert [move.player for move in persisted_moves] == [
                "X", "O", "X", "O", "X", "O", "X", "O", "X"
            ]
    finally:
        app.dependency_overrides.pop(get_game_service, None)
        _drop_schema(admin_engine, engine, schema)


def test_postgres_api_write_failure_rolls_back(monkeypatch):
    admin_engine, engine, schema = _new_schema()
    try:
        Base.metadata.create_all(engine)
        factory = _override_game_service(engine)
        original = SQLAlchemyGameUnitOfWork.persist_move

        def fail_after_staging(self, game_id, move, state):
            original(self, game_id, move, state)
            raise SQLAlchemyError("simulated database write failure")

        monkeypatch.setattr(
            SQLAlchemyGameUnitOfWork, "persist_move", fail_after_staging
        )
        with TestClient(app, raise_server_exceptions=False) as client:
            created = client.post(
                "/api/games", json={"mode": "HUMAN_VS_HUMAN"}
            )
            assert created.status_code == 201
            game_id = created.json()["id"]
            failed = client.post(
                f"/api/games/{game_id}/moves", json={"row": 4, "col": 5}
            )
            assert failed.status_code == 503

        with factory() as session:
            game = session.query(Game).filter_by(public_id=game_id).one()
            move_count = session.scalar(
                select(func.count())
                .select_from(Move)
                .where(Move.game_id == game.id)
            )
            assert move_count == 0
            assert game.status == GameStatus.IN_PROGRESS.value
            assert game.result is None
    finally:
        app.dependency_overrides.pop(get_game_service, None)
        _drop_schema(admin_engine, engine, schema)


def test_migration_backfills_existing_public_ids_and_is_idempotent():
    admin_engine, engine, schema = _new_schema()
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    """
                    CREATE TABLE games (
                        id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
                        mode VARCHAR(32) NOT NULL,
                        difficulty VARCHAR(16),
                        status VARCHAR(16) NOT NULL DEFAULT 'IN_PROGRESS',
                        result VARCHAR(16),
                        started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        ended_at TIMESTAMPTZ
                    )
                    """
                )
            )
            connection.execute(
                text(
                    "INSERT INTO games (mode) VALUES "
                    "('HUMAN_VS_HUMAN'), ('HUMAN_VS_AI')"
                )
            )
        assert run_migrations(engine) is True
        assert run_migrations(engine) is False
        with engine.connect() as connection:
            ids = connection.execute(
                text("SELECT public_id FROM games ORDER BY id")
            ).scalars().all()
            assert len(ids) == 2
            assert len(set(ids)) == 2
            assert all(str(UUID(value)) == value for value in ids)
            nullable = connection.execute(
                text(
                    "SELECT is_nullable FROM information_schema.columns "
                    "WHERE table_schema = current_schema() "
                    "AND table_name = 'games' AND column_name = 'public_id'"
                )
            ).scalar_one()
            assert nullable == "NO"
    finally:
        _drop_schema(admin_engine, engine, schema)


def test_migration_initializes_an_empty_database():
    admin_engine, engine, schema = _new_schema()
    try:
        assert run_migrations(engine) is True
        with engine.connect() as connection:
            tables = set(
                connection.execute(
                    text(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = current_schema()"
                    )
                ).scalars()
            )
            assert {"games", "moves", "game_analysis", "schema_migrations"} <= tables
            version = connection.execute(
                text(
                    "SELECT version FROM schema_migrations "
                    "WHERE version = '001_games_public_id'"
                )
            ).scalar_one()
            assert version == "001_games_public_id"
    finally:
        _drop_schema(admin_engine, engine, schema)

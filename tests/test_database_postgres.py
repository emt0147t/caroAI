"""PostgreSQL checks for the implemented SQLAlchemy schema.

Run only against a disposable PostgreSQL database. Schema DDL is disabled
unless the operator explicitly confirms the database is test-only.
"""

import os
import sys
import warnings
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

import scripts.production_qa_acceptance as production_qa

from app.api.dependencies import get_game_service
from app.main import app

from app.db.models import Base, Game, GameAnalysis, Move
from app.db.repository import SQLAlchemyGameRepository
from app.db.testing import validate_disposable_postgres_target
from app.domain.game_state import GameMode
from app.services.game_service import GameService


@pytest.fixture
def postgres_engine():
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL integration tests")
    if os.getenv("CAROAI_TEST_DATABASE_CONFIRMED") != "disposable-test-database":
        pytest.skip(
            "Schema DDL requires CAROAI_TEST_DATABASE_CONFIRMED="
            "disposable-test-database after verifying the target is disposable"
        )

    url = validate_disposable_postgres_target(
        database_url, os.getenv("CAROAI_TEST_DATABASE_CONFIRMED")
    )

    schema = f"caroai_test_{uuid4().hex}"
    admin_engine = create_engine(url, pool_pre_ping=True)
    schema_engine = None
    try:
        with admin_engine.begin() as connection:
            connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        schema_engine = create_engine(
            url,
            pool_pre_ping=True,
            connect_args={"options": f"-csearch_path={schema}"},
        )
        Base.metadata.create_all(schema_engine)
        yield schema_engine
    finally:
        active_test_error = sys.exc_info()[0] is not None
        if schema_engine is not None:
            schema_engine.dispose()
        try:
            with admin_engine.begin() as connection:
                connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
        except Exception as cleanup_error:
            if active_test_error:
                warnings.warn(
                    f"Could not clean up isolated schema {schema}: {cleanup_error!r}",
                    RuntimeWarning,
                )
            else:
                raise
        finally:
            admin_engine.dispose()


def test_game_and_ordered_moves_persist_across_sessions(postgres_engine):
    with Session(postgres_engine) as session:
        game = Game(mode="HUMAN_VS_HUMAN")
        session.add(game)
        session.flush()
        game_id = game.id
        session.add_all(
            [
                Move(game_id=game_id, player="X", row=0, col=0, move_number=1),
                Move(game_id=game_id, player="O", row=1, col=1, move_number=2),
            ]
        )
        session.commit()

    with Session(postgres_engine) as session:
        game = session.get(Game, game_id)
        moves = session.scalars(
            select(Move).where(Move.game_id == game_id).order_by(Move.move_number)
        ).all()

    assert game is not None
    assert [(move.player, move.row, move.col, move.move_number) for move in moves] == [
        ("X", 0, 0, 1), ("O", 1, 1, 2)
    ]


def test_move_number_is_unique_within_game(postgres_engine):
    with Session(postgres_engine) as session:
        game = Game(mode="HUMAN_VS_HUMAN")
        session.add(game)
        session.flush()
        session.add_all(
            [
                Move(game_id=game.id, player="X", row=0, col=0, move_number=1),
                Move(game_id=game.id, player="O", row=1, col=1, move_number=1),
            ]
        )
        with pytest.raises(IntegrityError):
            session.flush()
        session.rollback()


def test_move_requires_an_existing_game(postgres_engine):
    with Session(postgres_engine) as session:
        session.add(Move(game_id=999999, player="X", row=0, col=0, move_number=1))
        with pytest.raises(IntegrityError):
            session.flush()
        session.rollback()


@pytest.mark.parametrize(
    "values", [
        {"row": -1, "col": 0, "player": "X", "move_number": 1},
        {"row": 15, "col": 0, "player": "X", "move_number": 1},
        {"row": 0, "col": -1, "player": "X", "move_number": 1},
        {"row": 0, "col": 15, "player": "X", "move_number": 1},
        {"row": 0, "col": 0, "player": "Z", "move_number": 1},
        {"row": 0, "col": 0, "player": "X", "move_number": 0},
    ],
)
def test_move_check_constraints_reject_invalid_values(postgres_engine, values):
    with Session(postgres_engine) as session:
        game = Game(mode="HUMAN_VS_HUMAN")
        session.add(game)
        session.flush()
        session.add(Move(game_id=game.id, **values))
        with pytest.raises(IntegrityError):
            session.flush()
        session.rollback()


def test_analysis_coordinate_checks_and_nullable_move_id(postgres_engine):
    with Session(postgres_engine) as session:
        game = Game(mode="HUMAN_VS_HUMAN")
        session.add(game)
        session.flush()
        analysis = GameAnalysis(
            game_id=game.id, move_id=None, best_move_row=14, best_move_col=0
        )
        session.add(analysis)
        session.commit()
        analysis_id = analysis.id

    with Session(postgres_engine) as session:
        analysis = session.get(GameAnalysis, analysis_id)
        assert analysis is not None
        assert analysis.move_id is None
        assert (analysis.best_move_row, analysis.best_move_col) == (14, 0)

    with Session(postgres_engine) as session:
        game = Game(mode="HUMAN_VS_HUMAN")
        session.add(game)
        session.flush()
        session.add(GameAnalysis(game_id=game.id, best_move_row=15))
        with pytest.raises(IntegrityError):
            session.flush()
        session.rollback()


def test_constraint_failure_rolls_back_game_and_prior_move(postgres_engine):
    with Session(postgres_engine) as session:
        game = Game(mode="HUMAN_VS_HUMAN")
        session.add(game)
        session.flush()
        game_id = game.id
        session.add(Move(game_id=game_id, player="X", row=0, col=0, move_number=1))
        session.flush()
        session.add(Move(game_id=game_id, player="O", row=15, col=0, move_number=2))
        with pytest.raises(IntegrityError):
            session.flush()
        session.rollback()

    with Session(postgres_engine) as session:
        assert session.get(Game, game_id) is None
        assert session.scalar(
            select(func.count()).select_from(Move).where(Move.game_id == game_id)
        ) == 0


def test_qa_cleanup_is_run_scoped_and_removes_postgres_dependents(
    postgres_engine,
):
    qa_run_id = "a" * 32
    other_run_id = "b" * 32

    with Session(postgres_engine) as session:
        service = GameService(SQLAlchemyGameRepository(session))
        qa_game_id = service.create_game(
            GameMode.HUMAN_VS_HUMAN, qa_run_id=qa_run_id
        )
        other_game_id = service.create_game(
            GameMode.HUMAN_VS_HUMAN, qa_run_id=other_run_id
        )
        ordinary_game_id = service.create_game(GameMode.HUMAN_VS_HUMAN)

        service.make_move(qa_game_id, 0, 0)
        service.make_move(other_game_id, 1, 1)
        service.make_move(ordinary_game_id, 2, 2)

        qa_record = session.query(Game).filter_by(public_id=qa_game_id).one()
        qa_internal_id = qa_record.id
        qa_move = session.scalars(
            select(Move).where(Move.game_id == qa_internal_id)
        ).one()
        session.add(
            GameAnalysis(
                game_id=qa_internal_id,
                move_id=qa_move.id,
                best_move_row=0,
                best_move_col=1,
            )
        )
        session.commit()

    with Session(postgres_engine) as session:
        service = GameService(SQLAlchemyGameRepository(session))
        deleted_ids = service.delete_qa_run(qa_run_id)
        repeated_cleanup = service.delete_qa_run(qa_run_id)

    assert deleted_ids == [qa_game_id]
    assert repeated_cleanup == []

    with Session(postgres_engine) as session:
        assert session.query(Game).filter_by(public_id=qa_game_id).count() == 0
        assert session.query(Game).filter_by(public_id=other_game_id).count() == 1
        assert session.query(Game).filter_by(public_id=ordinary_game_id).count() == 1

        remaining_games = session.scalars(
            select(Game).where(
                Game.public_id.in_([other_game_id, ordinary_game_id])
            )
        ).all()
        remaining_internal_ids = {record.id for record in remaining_games}
        assert len(remaining_internal_ids) == 2
        assert session.scalar(
            select(func.count())
            .select_from(GameAnalysis)
            .where(GameAnalysis.game_id == qa_internal_id)
        ) == 0
        assert session.scalar(
            select(func.count()).select_from(Move)
            .where(Move.game_id == qa_internal_id)
        ) == 0
        assert session.scalar(
            select(func.count()).select_from(Move)
            .where(Move.game_id.in_(remaining_internal_ids))
        ) == 2

def test_production_qa_runner_over_real_postgres_api_and_exact_run_cleanup(
    postgres_engine, monkeypatch, capsys
):
    """Exercise the production runner through FastAPI and disposable PostgreSQL."""
    session_factory = sessionmaker(
        bind=postgres_engine,
        autoflush=False,
        expire_on_commit=False,
    )

    def postgres_game_service():
        with session_factory() as session:
            yield GameService(SQLAlchemyGameRepository(session))

    previous_override = app.dependency_overrides.get(get_game_service)
    app.dependency_overrides[get_game_service] = postgres_game_service
    other_run_id = uuid4().hex
    generated_run_ids = []

    def generate_run_token(_size):
        token = uuid4().hex
        generated_run_ids.append(token)
        return token

    monkeypatch.setenv("CAROAI_PUBLIC_URL", "https://caroai.example")
    monkeypatch.setattr(production_qa.secrets, "token_hex", generate_run_token)

    try:
        with TestClient(app) as client:
            other_created = client.post(
                "/api/qa/games",
                headers={"X-CaroAI-QA-Run-ID": other_run_id},
                json={"mode": "HUMAN_VS_HUMAN"},
            )
            assert other_created.status_code == 201
            other_game_id = other_created.json()["id"]
            other_move = client.post(
                f"/api/games/{other_game_id}/moves",
                json={"row": 2, "col": 3},
            )
            assert other_move.status_code == 200

            ordinary_created = client.post(
                "/api/games", json={"mode": "HUMAN_VS_HUMAN"}
            )
            assert ordinary_created.status_code == 201
            ordinary_game_id = ordinary_created.json()["id"]

            def call_real_api(
                base_url,
                method,
                path,
                *,
                run_id,
                payload=None,
                expected_status=(200,),
            ):
                response = client.request(
                    method,
                    base_url.rstrip("/") + path,
                    headers={"X-CaroAI-QA-Run-ID": run_id},
                    json=payload,
                )
                try:
                    body = response.json()
                except ValueError as exc:
                    raise production_qa.AcceptanceError(
                        f"{method} {path} returned non-JSON data "
                        f"(HTTP {response.status_code})"
                    ) from exc
                if response.status_code not in expected_status:
                    detail = (
                        body.get("detail", "no detail")
                        if isinstance(body, dict)
                        else "invalid body"
                    )
                    raise production_qa.AcceptanceError(
                        f"{method} {path} expected {expected_status}, "
                        f"received HTTP {response.status_code}: {detail}"
                    )
                if not isinstance(body, dict):
                    raise production_qa.AcceptanceError(
                        f"{method} {path} returned a non-object JSON value"
                    )
                return response.status_code, body

            monkeypatch.setattr(
                production_qa, "request_json", call_real_api
            )
            assert production_qa.main() == 0

            # The runner's own PvP/PvAI rows are deleted, while a second run
            # and a normal untagged game remain readable.
            assert client.get(f"/api/games/{other_game_id}").status_code == 200
            assert client.get(f"/api/games/{ordinary_game_id}").status_code == 200
            history = client.get("/api/history?limit=100&offset=0")
            assert history.status_code == 200
            history_ids = {item["id"] for item in history.json()["items"]}
            assert other_game_id in history_ids
            assert ordinary_game_id in history_ids

            other_cleanup = client.delete(
                "/api/qa/runs",
                headers={"X-CaroAI-QA-Run-ID": other_run_id},
            )
            assert other_cleanup.status_code == 200
            assert other_cleanup.json()["deleted_count"] == 1
            assert other_cleanup.json()["deleted_game_ids"] == [other_game_id]
            assert client.get(f"/api/games/{other_game_id}").status_code == 404

    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_game_service, None)
        else:
            app.dependency_overrides[get_game_service] = previous_override

    output = capsys.readouterr()
    assert "Production gameplay acceptance passed" in output.out
    assert "Production QA cleanup verified" in output.out
    assert generated_run_ids
    assert all(token not in output.out + output.err for token in generated_run_ids)

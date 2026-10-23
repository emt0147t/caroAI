"""PostgreSQL checks for the implemented SQLAlchemy schema.

Run only against a disposable PostgreSQL database. Schema DDL is disabled
unless the operator explicitly confirms the database is test-only.
"""

import os
import re
import sys
import warnings
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Base, Game, GameAnalysis, Move


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

    url = make_url(database_url)
    if url.get_backend_name() != "postgresql":
        pytest.fail("TEST_DATABASE_URL must use PostgreSQL")
    database_name = url.database or ""
    if not re.search(r"(^|[_-])test([_-]|$)", database_name, re.IGNORECASE):
        pytest.fail("TEST_DATABASE_URL database name must visibly identify a test database")
    if re.search(r"prod(uction)?|live", database_name, re.IGNORECASE):
        pytest.fail("Refusing schema DDL against a database name marked production/live")

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

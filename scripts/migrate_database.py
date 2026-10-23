"""Run versioned database migrations before the API starts."""

from pathlib import Path

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from app.db.database import get_engine
from app.db.models import Base


MIGRATION_VERSION = "001_games_public_id"
MIGRATION_PATH = (
    Path(__file__).resolve().parents[1]
    / "database"
    / "migrations"
    / "001_games_public_id.sql"
)


def run_migrations(engine: Engine) -> bool:
    """Apply pending migrations; return True when one was applied.

    An empty database is initialized from current metadata. Existing databases
    are altered only by versioned SQL migrations, not by create_all.
    """
    if not inspect(engine).has_table("games"):
        Base.metadata.create_all(engine)

    statements = [
        statement.strip()
        for statement in MIGRATION_PATH.read_text(encoding="utf-8").split(";")
        if statement.strip()
    ]
    with engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(128) PRIMARY KEY,
                    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                )
                """
            )
        )
        applied = connection.execute(
            text("SELECT 1 FROM schema_migrations WHERE version = :version"),
            {"version": MIGRATION_VERSION},
        ).first()
        if applied:
            return False

        for statement in statements:
            connection.exec_driver_sql(statement)
        connection.execute(
            text("INSERT INTO schema_migrations (version) VALUES (:version)"),
            {"version": MIGRATION_VERSION},
        )
    return True


def main() -> None:
    engine = get_engine()
    try:
        changed = run_migrations(engine)
        print(
            f"Applied migration: {MIGRATION_VERSION}"
            if changed
            else "Database schema is up to date."
        )
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()

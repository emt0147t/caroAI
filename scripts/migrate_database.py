"""Run versioned database migrations before the API starts."""

from pathlib import Path

from sqlalchemy import text
from sqlalchemy.engine import Engine

from app.db.database import get_engine


MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "database" / "migrations"


def run_migrations(engine: Engine) -> bool:
    """Apply each pending SQL migration in filename/version order.

    Production startup uses only explicit versioned SQL. SQLAlchemy metadata
    create_all is deliberately not used as an implicit migration mechanism.
    """
    changed = False
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
        for migration_path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            version = migration_path.stem
            applied = connection.execute(
                text("SELECT 1 FROM schema_migrations WHERE version = :version"),
                {"version": version},
            ).first()
            if applied:
                continue

            statements = [
                statement.strip()
                for statement in migration_path.read_text(encoding="utf-8").split(";")
                if statement.strip()
            ]
            for statement in statements:
                connection.exec_driver_sql(statement)
            connection.execute(
                text("INSERT INTO schema_migrations (version) VALUES (:version)"),
                {"version": version},
            )
            changed = True
            print(f"Applied migration: {version}")

    if not changed:
        print("Database schema is up to date.")
    return changed


def main() -> None:
    engine = get_engine()
    try:
        run_migrations(engine)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()

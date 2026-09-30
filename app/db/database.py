"""SQLAlchemy engine and session helpers.

The database URL is read from the ``DATABASE_URL`` environment variable.
This module does not load ``.env`` files; environment loading belongs to the
application/runtime configuration, which is not present in the repository yet.
"""

import os
from functools import lru_cache
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


DATABASE_URL_ENV = "DATABASE_URL"

# Keep the factory unbound so importing this module does not require a running
# database or a configured URL. A bound session is created by get_db().
SessionLocal = sessionmaker(autocommit=False, autoflush=False)


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Return the shared SQLAlchemy engine configured from DATABASE_URL."""
    database_url = os.getenv(DATABASE_URL_ENV)
    if not database_url:
        raise RuntimeError(
            f"Environment variable {DATABASE_URL_ENV} is required to connect to PostgreSQL."
        )

    return create_engine(database_url, pool_pre_ping=True)


def get_db() -> Generator[Session, None, None]:
    """Yield a session and always close it after the caller finishes."""
    session = SessionLocal(bind=get_engine())
    try:
        yield session
    finally:
        session.close()

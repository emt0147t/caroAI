"""Fail-closed validation for disposable PostgreSQL integration targets."""

import re

from sqlalchemy.engine import make_url


def validate_disposable_postgres_target(database_url: str | None, confirmation: str | None):
    """Validate the target before any engine creation or schema DDL."""
    if not database_url:
        raise ValueError("TEST_DATABASE_URL is required for PostgreSQL acceptance")
    if confirmation != "disposable-test-database":
        raise ValueError("Disposable PostgreSQL confirmation is required")

    url = make_url(database_url)
    if url.get_backend_name() != "postgresql":
        raise ValueError("TEST_DATABASE_URL must use PostgreSQL")

    database_name = url.database or ""
    if not re.search(r"(^|[_-])test([_-]|$)", database_name, re.IGNORECASE):
        raise ValueError("Database name must visibly identify a test database")
    if re.search(r"prod(uction)?|live", database_name, re.IGNORECASE):
        raise ValueError("Refusing schema DDL against production/live database")

    return url

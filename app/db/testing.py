"""Fail-closed validation for explicitly approved disposable PostgreSQL targets."""

import os
import re

from sqlalchemy.engine import make_url


ALLOWLIST_ENV = "CAROAI_TEST_POSTGRES_ALLOWLIST"


def validate_disposable_postgres_target(
    database_url: str | None, confirmation: str | None
):
    """Validate an exact host:port/database allowlist entry before engine creation."""
    if not database_url:
        raise ValueError("TEST_DATABASE_URL is required for PostgreSQL acceptance")
    if confirmation != "disposable-test-database":
        raise ValueError("Disposable PostgreSQL confirmation is required")

    url = make_url(database_url)
    if url.get_backend_name() != "postgresql":
        raise ValueError("TEST_DATABASE_URL must use PostgreSQL")

    # libpq connection parameters can override the URL authority. In particular,
    # psycopg2 accepts query-string host/hostaddr/port and service/servicefile
    # settings that can redirect the effective connection away from url.host.
    # Reject every query parameter (not just known routing keys) so newly added
    # libpq options cannot silently weaken this endpoint allowlist. Connection
    # options must be reviewed and modeled explicitly before being permitted.
    if url.query:
        parameter_names = ", ".join(sorted(str(key) for key in url.query))
        raise ValueError(
            "PostgreSQL URL query parameters are not permitted by the disposable "
            f"endpoint guard (found: {parameter_names})"
        )
    if url.fragment:
        raise ValueError("PostgreSQL URL fragments are not permitted")

    database_name = url.database or ""
    if not re.search(r"(^|[_-])test([_-]|$)", database_name, re.IGNORECASE):
        raise ValueError("Database name must visibly identify a test database")
    if re.search(r"prod(uction)?|live", database_name, re.IGNORECASE):
        raise ValueError("Refusing schema DDL against production/live database")

    host = (url.host or "").lower().rstrip(".")
    if not host:
        raise ValueError("PostgreSQL test endpoint must specify an explicit host")
    port = url.port or 5432
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    endpoint = f"{host}:{port}/{database_name}"

    configured_allowlist = os.getenv(ALLOWLIST_ENV, "")
    allowed_endpoints = {
        item.strip()
        for item in configured_allowlist.split(",")
        if item.strip()
    }
    if not allowed_endpoints:
        raise ValueError(
            f"{ALLOWLIST_ENV} must explicitly list approved host:port/database endpoints"
        )
    if endpoint not in allowed_endpoints:
        raise ValueError(
            f"PostgreSQL endpoint {endpoint!r} is not in {ALLOWLIST_ENV}"
        )

    return url

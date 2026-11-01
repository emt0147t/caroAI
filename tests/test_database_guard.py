"""Regression tests for the fail-closed PostgreSQL endpoint guard."""

import pytest

from app.db.testing import (
    ALLOWLIST_ENV,
    validate_disposable_postgres_target,
)


CONFIRMATION = "disposable-test-database"
LOCAL_URL = "postgresql+psycopg2://user:password@localhost:5432/caroai_test"


def test_unsafe_postgres_target_is_rejected(monkeypatch):
    monkeypatch.setenv(ALLOWLIST_ENV, "localhost:5432/caroai_test")
    cases = [
        (None, CONFIRMATION, "TEST_DATABASE_URL is required"),
        (LOCAL_URL, None, "confirmation is required"),
        (LOCAL_URL, "yes", "confirmation is required"),
        ("sqlite:///caroai_test.db", CONFIRMATION, "must use PostgreSQL"),
        (
            "postgresql://user:password@localhost:5432/caroai_dev",
            CONFIRMATION,
            "identify a test database",
        ),
        (
            "postgresql://user:password@localhost:5432/caroai_test_production",
            CONFIRMATION,
            "production/live",
        ),
        (
            "postgresql://user:password@localhost:5432/caroai_live_test",
            CONFIRMATION,
            "production/live",
        ),
    ]
    for database_url, confirmation, message in cases:
        with pytest.raises(ValueError, match=message):
            validate_disposable_postgres_target(database_url, confirmation)


def test_missing_endpoint_allowlist_fails_closed(monkeypatch):
    monkeypatch.delenv(ALLOWLIST_ENV, raising=False)

    with pytest.raises(ValueError, match="must explicitly list"):
        validate_disposable_postgres_target(LOCAL_URL, CONFIRMATION)


@pytest.mark.parametrize(
    "database_url",
    [
        "postgresql://user:password@remote-production-host:5432/caroai_test",
        "postgresql://user:password@localhost:5433/caroai_test",
        "postgresql://user:password@127.0.0.1:5432/caroai_test",
    ],
)
def test_unapproved_host_or_port_is_rejected(monkeypatch, database_url):
    monkeypatch.setenv(ALLOWLIST_ENV, "localhost:5432/caroai_test")

    with pytest.raises(ValueError, match="is not in"):
        validate_disposable_postgres_target(database_url, CONFIRMATION)


@pytest.mark.parametrize(
    "routing_query",
    [
        "host=remote-production-host",
        "host=remote-a,remote-b",
        "hostaddr=203.0.113.10",
        "port=5433",
        "service=production",
        "servicefile=/tmp/pg_service.conf",
        "dbname=other_database",
        "options=-csearch_path=public",
    ],
)
def test_libpq_query_parameters_cannot_override_approved_endpoint(
    monkeypatch, routing_query
):
    monkeypatch.setenv(ALLOWLIST_ENV, "localhost:5432/caroai_test")
    database_url = f"{LOCAL_URL}?{routing_query}"

    with pytest.raises(ValueError, match="query parameters are not permitted"):
        validate_disposable_postgres_target(database_url, CONFIRMATION)


@pytest.mark.parametrize(
    ("database_url", "allowlist_entry"),
    [
        (LOCAL_URL, "localhost:5432/caroai_test"),
        (
            "postgresql://user:password@127.0.0.1:5432/caroai_test",
            "127.0.0.1:5432/caroai_test",
        ),
    ],
)
def test_url_fragment_is_rejected_even_for_allowlisted_authority(monkeypatch):
    monkeypatch.setenv(ALLOWLIST_ENV, "localhost:5432/caroai_test")

    with pytest.raises(ValueError, match="fragments are not permitted"):
        validate_disposable_postgres_target(
            f"{LOCAL_URL}#host=remote-production-host", CONFIRMATION
        )


def test_explicitly_allowlisted_local_disposable_target_is_accepted(
    monkeypatch, database_url, allowlist_entry
):
    monkeypatch.setenv(ALLOWLIST_ENV, allowlist_entry)

    url = validate_disposable_postgres_target(database_url, CONFIRMATION)

    assert url.get_backend_name() == "postgresql"
    assert url.database == "caroai_test"

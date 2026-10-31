"""Negative-path regression tests for the PostgreSQL safety guard."""

import pytest

from app.db.testing import validate_disposable_postgres_target


VALID_URL = "postgresql+psycopg2://user:password@localhost:5432/caroai_test"
CONFIRMATION = "disposable-test-database"


@pytest.mark.parametrize(
    ("database_url", "confirmation", "message"),
    [
        (None, CONFIRMATION, "TEST_DATABASE_URL is required"),
        (VALID_URL, None, "confirmation is required"),
        (VALID_URL, "yes", "confirmation is required"),
        (
            "sqlite:///caroai_test.db",
            CONFIRMATION,
            "must use PostgreSQL",
        ),
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
    ],
)
def test_unsafe_postgres_target_is_rejected(database_url, confirmation, message):
    with pytest.raises(ValueError, match=message):
        validate_disposable_postgres_target(database_url, confirmation)


def test_confirmed_disposable_postgres_test_database_is_accepted():
    url = validate_disposable_postgres_target(VALID_URL, CONFIRMATION)

    assert url.get_backend_name() == "postgresql"
    assert url.database == "caroai_test"

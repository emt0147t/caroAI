"""Regression tests for DATABASE_URL driver normalization."""

import pytest

from app.db.database import normalize_database_url


@pytest.mark.parametrize(
    ("input_url", "expected_url"),
    [
        (
            "postgresql://user:password@db:5432/caroai",
            "postgresql+psycopg2://user:password@db:5432/caroai",
        ),
        (
            "postgres://user:password@db:5432/caroai",
            "postgresql+psycopg2://user:password@db:5432/caroai",
        ),
        (
            "postgresql+psycopg2://user:password@db:5432/caroai",
            "postgresql+psycopg2://user:password@db:5432/caroai",
        ),
        (
            "postgresql+psycopg://user:password@db:5432/caroai",
            "postgresql+psycopg://user:password@db:5432/caroai",
        ),
    ],
)
def test_normalize_database_url_uses_installed_driver(input_url, expected_url):
    assert normalize_database_url(input_url) == expected_url

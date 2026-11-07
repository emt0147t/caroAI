import pytest

from app.api.qa_security import (
    MAX_QA_REQUESTS_PER_MINUTE,
    MAX_QA_TOTAL_REQUESTS_PER_MINUTE_PER_PROCESS,
    QARequestLimiter,
    acquire_qa_operation,
    capability_for_run,
    load_qa_config,
    verify_capability,
)


SECRET = b"s" * 32


def test_qa_security_is_disabled_without_explicit_opt_in(monkeypatch):
    monkeypatch.delenv("CAROAI_QA_ENABLED", raising=False)
    monkeypatch.delenv("CAROAI_QA_HMAC_SECRET", raising=False)

    assert load_qa_config() is None


@pytest.mark.parametrize(
    "enabled,secret",
    [
        ("yes", SECRET.decode()),
        ("true", "too-short"),
        ("true", ""),
    ],
)
def test_invalid_qa_security_configuration_fails_closed(
    monkeypatch, enabled, secret
):
    monkeypatch.setenv("CAROAI_QA_ENABLED", enabled)
    monkeypatch.setenv("CAROAI_QA_HMAC_SECRET", secret)

    assert load_qa_config() is None


def test_valid_capability_is_bound_to_run_and_expiry():
    capability = capability_for_run("a" * 32, 1_700_000_100, SECRET)

    assert verify_capability("a" * 32, capability, SECRET, now=1_700_000_000)
    assert not verify_capability("b" * 32, capability, SECRET, now=1_700_000_000)
    assert not verify_capability("a" * 32, capability, b"x" * 32, now=1_700_000_000)
    assert not verify_capability("a" * 32, capability, SECRET, now=1_700_000_101)


@pytest.mark.parametrize("capability", ["", "bad", "v1.nope.signature"])
def test_malformed_capability_is_rejected(capability):
    assert not verify_capability("a" * 32, capability, SECRET, now=1_700_000_000)


def test_capability_lifetime_is_bounded():
    capability = capability_for_run("a" * 32, 1_700_001_000, SECRET)

    assert not verify_capability("a" * 32, capability, SECRET, now=1_700_000_000)


def test_qa_request_limiter_blocks_over_limit_and_resets_after_window():
    limiter = QARequestLimiter()

    assert all(
        limiter.allow("a" * 32, now=10.0 + index / 100)
        for index in range(MAX_QA_REQUESTS_PER_MINUTE)
    )
    assert not limiter.allow("a" * 32, now=11.0)
    assert limiter.allow("a" * 32, now=71.0)


def test_qa_request_limiter_enforces_process_wide_limit_across_runs():
    limiter = QARequestLimiter(limit=MAX_QA_REQUESTS_PER_MINUTE + 1)

    assert all(
        limiter.allow(f"{index:032x}", now=10.0)
        for index in range(MAX_QA_TOTAL_REQUESTS_PER_MINUTE_PER_PROCESS)
    )
    assert not limiter.allow("f" * 32, now=10.0)


def test_concurrent_qa_operation_limit_is_process_local_and_bounded():
    with acquire_qa_operation() as first, acquire_qa_operation() as second:
        assert first is True
        assert second is True
        with acquire_qa_operation() as third:
            assert third is False

    with acquire_qa_operation() as released_slot:
        assert released_slot is True

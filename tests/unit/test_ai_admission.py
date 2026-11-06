import pytest

from app.ai.admission import (
    AIAdmissionRejectedError,
    ImpossibleAdmissionGuard,
)


def test_impossible_guard_rejects_when_capacity_is_full_and_wait_is_zero():
    guard = ImpossibleAdmissionGuard(max_concurrency=1, queue_wait_ms=0)

    with guard.acquire():
        with pytest.raises(AIAdmissionRejectedError):
            with guard.acquire():
                pass


def test_impossible_guard_allows_next_search_after_release():
    guard = ImpossibleAdmissionGuard(max_concurrency=1, queue_wait_ms=0)

    with guard.acquire():
        pass

    with guard.acquire():
        assert True


def test_zero_limit_disables_admission_guard():
    guard = ImpossibleAdmissionGuard(max_concurrency=0, queue_wait_ms=0)

    with guard.acquire():
        with guard.acquire():
            assert True


def test_impossible_guard_respects_bounded_queue_wait():
    guard = ImpossibleAdmissionGuard(max_concurrency=1, queue_wait_ms=1)

    with guard.acquire():
        with pytest.raises(AIAdmissionRejectedError):
            with guard.acquire():
                pass

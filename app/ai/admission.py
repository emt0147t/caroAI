"""Process-local admission control for expensive IMPOSSIBLE searches."""

from contextlib import contextmanager
import os
from threading import BoundedSemaphore, Lock
from typing import Iterator


class AIAdmissionRejectedError(RuntimeError):
    """Raised when the configured IMPOSSIBLE search capacity is exhausted."""


class ImpossibleAdmissionGuard:
    """Bound concurrent IMPOSSIBLE searches in one Python process."""

    def __init__(self, max_concurrency: int = 0, queue_wait_ms: int = 0) -> None:
        if max_concurrency < 0:
            raise ValueError("max_concurrency must be non-negative")
        if queue_wait_ms < 0:
            raise ValueError("queue_wait_ms must be non-negative")
        self.max_concurrency = max_concurrency
        self.queue_wait_ms = queue_wait_ms
        self._semaphore = (
            BoundedSemaphore(max_concurrency) if max_concurrency > 0 else None
        )

    @classmethod
    def from_environment(cls) -> "ImpossibleAdmissionGuard":
        try:
            maximum = int(os.getenv("CAROAI_IMPOSSIBLE_MAX_CONCURRENCY", "0"))
            wait_ms = int(os.getenv("CAROAI_IMPOSSIBLE_QUEUE_WAIT_MS", "0"))
        except ValueError as exc:
            raise ValueError("IMPOSSIBLE admission settings must be integers") from exc
        return cls(maximum, wait_ms)

    @contextmanager
    def acquire(self) -> Iterator[None]:
        """Acquire capacity or fail with a typed error after the configured wait."""
        if self._semaphore is None:
            yield
            return

        if self.queue_wait_ms == 0:
            acquired = self._semaphore.acquire(blocking=False)
        else:
            acquired = self._semaphore.acquire(timeout=self.queue_wait_ms / 1000.0)

        if not acquired:
            raise AIAdmissionRejectedError(
                "IMPOSSIBLE search capacity is currently full; retry shortly"
            )

        try:
            yield
        finally:
            self._semaphore.release()


_default_guard: ImpossibleAdmissionGuard | None = None
_default_guard_lock = Lock()


def get_default_impossible_admission_guard() -> ImpossibleAdmissionGuard:
    """Return the one process-wide guard shared by all request-scoped services."""
    global _default_guard
    if _default_guard is None:
        with _default_guard_lock:
            if _default_guard is None:
                _default_guard = ImpossibleAdmissionGuard.from_environment()
    return _default_guard

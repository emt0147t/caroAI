"""Fail-closed configuration and process-local guards for production QA routes."""

from collections import defaultdict, deque
from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import hmac
import os
import re
import threading
import time
from typing import Iterator


CAPABILITY_TTL_SECONDS = 600
MIN_SECRET_BYTES = 32
MAX_QA_GAMES_PER_RUN = 2
MAX_QA_REQUESTS_PER_MINUTE = 10
MAX_QA_TOTAL_REQUESTS_PER_MINUTE_PER_PROCESS = 30
MAX_TRACKED_RUNS = 1024
MAX_CONCURRENT_QA_OPERATIONS_PER_PROCESS = 2

_RUN_ID_RE = re.compile(r"^[0-9a-f]{32}$")
_CAPABILITY_RE = re.compile(r"^v1\.([0-9]{1,12})\.([0-9a-f]{64})$")


@dataclass(frozen=True)
class QAConfig:
    """Validated configuration; an absent value means QA must stay disabled."""

    hmac_secret: bytes


def load_qa_config() -> QAConfig | None:
    """Load explicit opt-in configuration, failing closed on any invalid value."""
    enabled = os.getenv("CAROAI_QA_ENABLED")
    if enabled != "true":
        return None

    secret = os.getenv("CAROAI_QA_HMAC_SECRET", "").encode("utf-8")
    if len(secret) < MIN_SECRET_BYTES:
        return None
    return QAConfig(hmac_secret=secret)


def _signature(run_id: str, expires_at: int, secret: bytes) -> str:
    message = f"caroai-qa:v1:{run_id}:{expires_at}".encode("ascii")
    return hmac.new(secret, message, hashlib.sha256).hexdigest()


def capability_for_run(run_id: str, expires_at: int, secret: bytes) -> str:
    """Create a signed capability for a run, without exposing the secret."""
    if not _RUN_ID_RE.fullmatch(run_id):
        raise ValueError("QA run ID has an invalid format")
    if not isinstance(expires_at, int) or isinstance(expires_at, bool):
        raise ValueError("QA capability expiry must be an integer timestamp")
    if len(secret) < MIN_SECRET_BYTES:
        raise ValueError("QA capability secret is not configured securely")
    return f"v1.{expires_at}.{_signature(run_id, expires_at, secret)}"


def create_qa_capability(
    run_id: str, secret: bytes, *, now: int | None = None
) -> str:
    """Create a capability that expires within the configured short TTL."""
    issued_at = int(time.time()) if now is None else now
    return capability_for_run(
        run_id, issued_at + CAPABILITY_TTL_SECONDS, secret
    )


def verify_capability(
    run_id: str,
    capability: str,
    secret: bytes,
    *,
    now: int | None = None,
) -> bool:
    """Validate format, exact run scope, signature, and short expiry window."""
    if not _RUN_ID_RE.fullmatch(run_id) or len(secret) < MIN_SECRET_BYTES:
        return False
    match = _CAPABILITY_RE.fullmatch(capability)
    if match is None:
        return False

    expires_at = int(match.group(1))
    current_time = int(time.time()) if now is None else now
    remaining = expires_at - current_time
    if remaining <= 0 or remaining > CAPABILITY_TTL_SECONDS:
        return False

    expected = _signature(run_id, expires_at, secret)
    return hmac.compare_digest(match.group(2), expected)


class QARequestLimiter:
    """Sliding-window limit for QA control routes, local to this process."""

    def __init__(
        self,
        limit: int = MAX_QA_REQUESTS_PER_MINUTE,
        global_limit: int = MAX_QA_TOTAL_REQUESTS_PER_MINUTE_PER_PROCESS,
    ) -> None:
        self._limit = limit
        self._global_limit = global_limit
        self._lock = threading.Lock()
        self._requests: dict[str, deque[float]] = defaultdict(deque)
        self._global_requests: deque[float] = deque()

    def allow(self, run_id: str, *, now: float | None = None) -> bool:
        current_time = time.monotonic() if now is None else now
        with self._lock:
            expired_before = current_time - 60
            while (
                self._global_requests
                and self._global_requests[0] <= expired_before
            ):
                self._global_requests.popleft()
            for tracked_run, requests in list(self._requests.items()):
                while requests and requests[0] <= expired_before:
                    requests.popleft()
                if not requests:
                    del self._requests[tracked_run]

            requests = self._requests.get(run_id)
            if requests is None:
                if len(self._requests) >= MAX_TRACKED_RUNS:
                    return False
                requests = self._requests[run_id]
            if (
                len(requests) >= self._limit
                or len(self._global_requests) >= self._global_limit
            ):
                return False
            requests.append(current_time)
            self._global_requests.append(current_time)
            return True


_qa_operation_semaphore = threading.BoundedSemaphore(
    MAX_CONCURRENT_QA_OPERATIONS_PER_PROCESS
)


@contextmanager
def acquire_qa_operation() -> Iterator[bool]:
    """Try to acquire one QA control slot; the limit is per process only."""
    acquired = _qa_operation_semaphore.acquire(blocking=False)
    try:
        yield acquired
    finally:
        if acquired:
            _qa_operation_semaphore.release()

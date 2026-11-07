"""Run the API with opt-in Phase B benchmark instrumentation."""

from __future__ import annotations

import contextvars
import json
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.main import app
from app.services import game_service


_request_metrics: contextvars.ContextVar[dict | None] = contextvars.ContextVar(
    "caroai_benchmark_request_metrics", default=None
)
_write_lock = threading.Lock()
_metrics_path = Path(os.environ["CAROAI_BENCHMARK_SERVER_METRICS"])


def _write_record(record: dict) -> None:
    _metrics_path.parent.mkdir(parents=True, exist_ok=True)
    with _write_lock, _metrics_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, separators=(",", ":")) + "\n")


class BenchmarkMetricsMiddleware:
    def __init__(self, application, run_id: str) -> None:
        self.application = application
        self.run_id = run_id

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.application(scope, receive, send)
            return

        request_id = next(
            (
                value.decode("latin-1")
                for name, value in scope.get("headers", [])
                if name.lower() == b"x-request-id"
            ),
            str(uuid.uuid4()),
        )
        metrics = {
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "run_id": self.run_id,
            "request_id": request_id,
            "http_method": scope.get("method"),
            "endpoint": scope.get("path"),
            "api_server_ms": None,
            "engine_search_ms": None,
            "row_lock_query_ms": None,
            "transaction_duration_ms": 0.0,
            "transaction_count": 0,
            "db_connection_hold_ms": 0.0,
            "db_backend_pids": [],
            "http_status": None,
        }
        token = _request_metrics.set(metrics)
        started = time.perf_counter_ns()

        async def capture_status(message):
            if message["type"] == "http.response.start":
                metrics["http_status"] = message["status"]
                message.setdefault("headers", []).append(
                    (b"x-request-id", request_id.encode("latin-1"))
                )
            await send(message)

        try:
            await self.application(scope, receive, capture_status)
        finally:
            metrics["api_server_ms"] = (time.perf_counter_ns() - started) / 1e6
            _write_record(metrics)
            _request_metrics.reset(token)


def _engine_wrapper(*args, **kwargs):
    metrics = _request_metrics.get()
    started = time.perf_counter_ns()
    try:
        return _original_engine(*args, **kwargs)
    finally:
        if metrics is not None:
            metrics["engine_search_ms"] = (time.perf_counter_ns() - started) / 1e6


_original_engine = game_service.run_ai_engine
game_service.run_ai_engine = _engine_wrapper


@event.listens_for(Engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    metrics = _request_metrics.get()
    if metrics is not None and "for update" in statement.lower():
        context._caroai_row_lock_started_ns = time.perf_counter_ns()


@event.listens_for(Engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    metrics = _request_metrics.get()
    started = getattr(context, "_caroai_row_lock_started_ns", None)
    if metrics is not None and started is not None:
        metrics["row_lock_query_ms"] = (time.perf_counter_ns() - started) / 1e6


@event.listens_for(Engine, "checkout")
def _checkout(dbapi_connection, connection_record, connection_proxy):
    metrics = _request_metrics.get()
    if metrics is None:
        return
    connection_record.info["caroai_checkout_ns"] = time.perf_counter_ns()
    try:
        metrics["db_backend_pids"].append(dbapi_connection.get_backend_pid())
    except (AttributeError, TypeError):
        pass


@event.listens_for(Engine, "checkin")
def _checkin(dbapi_connection, connection_record):
    metrics = _request_metrics.get()
    started = connection_record.info.pop("caroai_checkout_ns", None)
    if metrics is not None and started is not None:
        metrics["db_connection_hold_ms"] += (time.perf_counter_ns() - started) / 1e6


@event.listens_for(Session, "after_begin")
def _transaction_begin(session, transaction, connection):
    if transaction.parent is None:
        metrics = _request_metrics.get()
        if metrics is not None:
            metrics["_transaction_started_ns"] = time.perf_counter_ns()


@event.listens_for(Session, "after_transaction_end")
def _transaction_end(session, transaction):
    if transaction.parent is None:
        metrics = _request_metrics.get()
        if metrics is not None:
            started = metrics.pop("_transaction_started_ns", None)
            if started is not None:
                elapsed_ms = (time.perf_counter_ns() - started) / 1e6
                metrics["transaction_duration_ms"] = (
                    metrics.get("transaction_duration_ms", 0.0) + elapsed_ms
                )
                metrics["transaction_count"] = metrics.get("transaction_count", 0) + 1


run_id = os.environ.get("CAROAI_BENCHMARK_RUN_ID", "phase-b")
app.add_middleware(BenchmarkMetricsMiddleware, run_id=run_id)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=os.environ.get("HOST", "127.0.0.1"),
        port=int(os.environ.get("PORT", "18000")),
        log_level="warning",
    )

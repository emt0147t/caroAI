"""Low-cardinality Prometheus metrics for CaroAI application and database work."""

from __future__ import annotations

import re
import time
from typing import Any

from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


HTTP_REQUESTS = Counter(
    "caroai_http_requests_total",
    "Completed HTTP requests by normalized route and status.",
    ("method", "route", "status"),
)
HTTP_DURATION = Histogram(
    "caroai_http_request_duration_seconds",
    "HTTP request duration by normalized route.",
    ("method", "route"),
)
AI_SEARCH_DURATION = Histogram(
    "caroai_ai_search_duration_seconds",
    "AI engine search duration.",
    ("difficulty", "outcome"),
)
AI_SEARCH_NODES = Histogram(
    "caroai_ai_search_nodes",
    "Minimax nodes visited per AI request.",
    ("difficulty",),
    buckets=(1, 10, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 50000, 100000),
)
AI_BRANCHING_FACTOR = Histogram(
    "caroai_ai_average_branching_factor",
    "Average post-candidate-cap branching factor per search.",
    ("difficulty",),
)
AI_ALPHA_BETA_PRUNING = Histogram(
    "caroai_ai_alpha_beta_pruning_rate",
    "Share of post-cap candidates skipped by alpha-beta cutoffs.",
    ("difficulty",),
)
AI_CANDIDATE_CAP_PRUNING = Histogram(
    "caroai_ai_candidate_cap_pruning_rate",
    "Share of generated candidates removed by the configured candidate cap.",
    ("difficulty",),
)
AI_TIMEOUTS = Counter(
    "caroai_ai_search_timeouts_total",
    "AI searches that returned a legal fallback after their time budget expired.",
    ("difficulty",),
)
DB_CHECKED_OUT = Gauge(
    "caroai_db_connections_checked_out",
    "SQLAlchemy DBAPI connections currently checked out by this process.",
)
DB_CONNECTION_HOLD = Histogram(
    "caroai_db_connection_hold_seconds",
    "Time a SQLAlchemy DBAPI connection remains checked out.",
)
DB_STATEMENT_DURATION = Histogram(
    "caroai_db_statement_duration_seconds",
    "SQL statement execution duration, grouped by operation and row-lock flag.",
    ("operation", "row_lock"),
)
DB_TRANSACTION_DURATION = Histogram(
    "caroai_db_transaction_duration_seconds",
    "Root SQLAlchemy transaction duration.",
)


def normalize_route(path: str) -> str:
    """Map request paths to a small route vocabulary; never expose identifiers."""
    if path in {
        "/health", "/ready", "/metrics", "/", "/history.html",
        "/api/history", "/api/games", "/api/qa/games", "/api/qa/runs",
    }:
        return path
    if re.fullmatch(r"/api/games/[^/]+", path):
        return "/api/games/{game_id}"
    if re.fullmatch(r"/api/games/[^/]+/moves", path):
        return "/api/games/{game_id}/moves"
    if re.fullmatch(r"/api/games/[^/]+/ai-move", path):
        return "/api/games/{game_id}/ai-move"
    return "unmatched"


class HTTPMetricsMiddleware:
    """Pure ASGI middleware with route normalization and bounded labels."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if path == "/metrics":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "OTHER").upper()
        if method not in {"GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"}:
            method = "OTHER"
        route = normalize_route(path)
        status_code = 500
        started = time.perf_counter()

        async def capture_status(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
            await send(message)

        try:
            await self.app(scope, receive, capture_status)
        finally:
            elapsed = max(0.0, time.perf_counter() - started)
            HTTP_REQUESTS.labels(method, route, str(status_code)).inc()
            HTTP_DURATION.labels(method, route).observe(elapsed)


def record_ai_search(difficulty: str, result: dict[str, Any]) -> None:
    """Record an engine result without adding game or request identifiers as labels."""
    key = difficulty.lower()
    elapsed = max(0.0, float(result.get("elapsed_ms", 0.0)) / 1000.0)
    stats = result.get("search_stats") or {}
    timed_out = bool(stats.get("timed_out", False))
    shortcut = stats.get("shortcut", "none")
    outcome = "timeout" if timed_out else (
        "tactical_shortcut" if shortcut in {"immediate_win", "forced_block"}
        else "search"
    )
    AI_SEARCH_DURATION.labels(key, outcome).observe(elapsed)
    AI_SEARCH_NODES.labels(key).observe(max(0, int(stats.get("nodes", 0))))
    AI_BRANCHING_FACTOR.labels(key).observe(
        max(0.0, float(stats.get("average_branching_factor", 0.0)))
    )
    AI_ALPHA_BETA_PRUNING.labels(key).observe(
        min(1.0, max(0.0, float(stats.get("alpha_beta_pruning_rate", 0.0))))
    )
    AI_CANDIDATE_CAP_PRUNING.labels(key).observe(
        min(1.0, max(0.0, float(stats.get("candidate_cap_pruning_rate", 0.0))))
    )
    if timed_out:
        AI_TIMEOUTS.labels(key).inc()


def _sql_operation(statement: str) -> str:
    first = statement.lstrip().split(None, 1)[0].upper() if statement.strip() else ""
    return first if first in {"SELECT", "INSERT", "UPDATE", "DELETE"} else "OTHER"


@event.listens_for(Engine, "before_cursor_execute")
def _before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._caroai_metrics_started = time.perf_counter()
    context._caroai_metrics_operation = _sql_operation(statement)
    context._caroai_metrics_row_lock = "FOR UPDATE" in statement.upper()


@event.listens_for(Engine, "after_cursor_execute")
def _after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    started = getattr(context, "_caroai_metrics_started", None)
    if started is None:
        return
    DB_STATEMENT_DURATION.labels(
        getattr(context, "_caroai_metrics_operation", "OTHER"),
        str(bool(getattr(context, "_caroai_metrics_row_lock", False))).lower(),
    ).observe(max(0.0, time.perf_counter() - started))


@event.listens_for(Engine, "checkout")
def _connection_checkout(dbapi_connection, connection_record, connection_proxy):
    connection_record.info["caroai_metrics_checkout"] = time.perf_counter()
    DB_CHECKED_OUT.inc()


@event.listens_for(Engine, "checkin")
def _connection_checkin(dbapi_connection, connection_record):
    started = connection_record.info.pop("caroai_metrics_checkout", None)
    DB_CHECKED_OUT.dec()
    if started is not None:
        DB_CONNECTION_HOLD.observe(max(0.0, time.perf_counter() - started))


@event.listens_for(Session, "after_begin")
def _transaction_begin(session, transaction, connection):
    if transaction.parent is None:
        session.info["caroai_metrics_transaction_started"] = time.perf_counter()


@event.listens_for(Session, "after_transaction_end")
def _transaction_end(session, transaction):
    if transaction.parent is None:
        started = session.info.pop("caroai_metrics_transaction_started", None)
        if started is not None:
            DB_TRANSACTION_DURATION.observe(
                max(0.0, time.perf_counter() - started)
            )


def install_observability(app: FastAPI) -> None:
    """Install bounded-label middleware and expose /metrics once per app."""
    if getattr(app.state, "caroai_observability_installed", False):
        return
    app.add_middleware(HTTPMetricsMiddleware)

    def metrics_endpoint():
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST,
        )

    app.add_route("/metrics", metrics_endpoint, methods=["GET"], include_in_schema=False)
    app.state.caroai_observability_installed = True

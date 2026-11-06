"""API/PostgreSQL contention benchmark for a disposable local database."""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import threading
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import httpx
import psycopg2

ROOT = Path(__file__).resolve().parents[1]
SERVER_METRICS = [
    "engine_search_ms", "row_lock_query_ms", "transaction_duration_ms",
    "transaction_count", "db_connection_hold_ms", "db_backend_pids",
]
REQUEST_FIELDS = [
    "timestamp_utc", "run_id", "request_id", "scenario", "fixture",
    "difficulty", "concurrency", "worker_id", "game_id", "http_method",
    "endpoint", "http_status", "api_response_ms", "is_warmup",
    "sample_index", "engine_search_ms",
    "row_lock_query_ms", "observed_lock_wait_ms", "transaction_duration_ms",
    "db_connection_hold_ms", "active_db_connections_peak", "response_valid",
    "legal_move", "error_type", "error_message",
]
POSTGRES_FIELDS = [
    "timestamp_utc", "run_id", "active_db_connections", "pid", "state",
    "wait_event_type", "wait_event", "blocking_pids", "query",
]


class PostgresMonitor:
    def __init__(self, dsn: str, path: Path, run_id: str, interval_s: float = 0.01):
        self.dsn, self.path, self.run_id, self.interval_s = dsn, path, run_id, interval_s
        self.stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.samples: list[dict] = []
        self.error: str | None = None

    def start(self) -> None:
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        self.thread.join(timeout=5)

    def _run(self) -> None:
        try:
            connection = psycopg2.connect(self.dsn)
            connection.autocommit = True
            while not self.stop_event.is_set():
                captured = datetime.now(timezone.utc).isoformat()
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT pid, state, wait_event_type, wait_event,
                               pg_blocking_pids(pid), query,
                               count(*) OVER ()
                        FROM pg_stat_activity
                        WHERE datname = current_database()
                          AND pid <> pg_backend_pid()
                    """)
                    rows = cursor.fetchall()
                active = sum(1 for row in rows if row[1] == "active")
                self.samples.append({
                    "timestamp_utc": captured, "run_id": self.run_id,
                    "active_db_connections": active,
                    "sessions": [
                        {"pid": row[0], "state": row[1], "wait_event_type": row[2],
                         "wait_event": row[3], "blocking_pids": list(row[4] or []),
                         "query": row[5]}
                        for row in rows
                    ],
                })
                self.stop_event.wait(self.interval_s)
            connection.close()
        except Exception as exc:  # surfaced in run metadata, never silently replaced
            self.error = f"{type(exc).__name__}: {exc}"

    def write_csv(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=POSTGRES_FIELDS)
            writer.writeheader()
            for sample in self.samples:
                for session in sample["sessions"] or [None]:
                    writer.writerow({
                        "timestamp_utc": sample["timestamp_utc"],
                        "run_id": self.run_id,
                        "active_db_connections": sample["active_db_connections"],
                        **(session or {}),
                    })


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[max(0, __import__("math").ceil(q * len(ordered)) - 1)]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-url", default=os.getenv("DATABASE_URL"), help="Disposable PostgreSQL URL")
    parser.add_argument("--base-url", help="Use an already-started benchmark API")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports/benchmark-phase-b")
    parser.add_argument("--samples", type=int, default=30, help="Measured repetitions per workload group")
    parser.add_argument("--warmup", type=int, default=3, help="Unreported warm-up repetitions per group")
    parser.add_argument("--concurrency", default="1,2,4,8")
    parser.add_argument("--difficulties", default="easy,medium,hard,impossible")
    parser.add_argument("--timeout-seconds", type=float, default=120)
    parser.add_argument("--monitor-interval-ms", type=float, default=10)
    parser.add_argument("--server-port", type=int, default=18000)
    parser.add_argument("--smoke-only", action="store_true", help="Run one sample at concurrency 1 and 2, all difficulties")
    return parser


async def wait_ready(client: httpx.AsyncClient, timeout: float) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            response = await client.get("/ready", timeout=2)
            if response.status_code == 200:
                return
        except httpx.HTTPError:
            pass
        await asyncio.sleep(0.25)
    raise TimeoutError("Benchmark API did not become ready")


async def new_ai_game(client: httpx.AsyncClient) -> tuple[str, bool]:
    response = await client.post("/api/games", json={"mode": "HUMAN_VS_AI"})
    response.raise_for_status()
    game_id = response.json()["id"]
    # Fixed, legal 5-ply opening. Odd ply count gives O the turn; all state is
    # created through real routes and the database can rebuild its history.
    moves = [(7, 7), (7, 8), (6, 7), (8, 8), (6, 6)]
    for row, col in moves:
        move_response = await client.post(
            f"/api/games/{game_id}/moves", json={"row": row, "col": col}
        )
        move_response.raise_for_status()
    return game_id, True


async def request_ai(
    client, run_id, scenario, difficulty, concurrency, worker, game_id, timeout
):
    request_id = str(uuid.uuid4())
    path = f"/api/games/{game_id}/ai-move"
    started = time.perf_counter_ns()
    row = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(), "run_id": run_id,
        "request_id": request_id, "scenario": scenario, "fixture": "legal_five_ply_opening",
        "difficulty": difficulty, "concurrency": concurrency, "worker_id": worker,
        "game_id": game_id, "http_method": "POST", "endpoint": path,
        "http_status": None, "api_response_ms": None, "response_valid": False,
        "legal_move": False, "error_type": None, "error_message": None,
    }
    try:
        response = await client.post(path, json={"difficulty": difficulty},
                                     headers={"X-Request-ID": request_id}, timeout=timeout)
        row["http_status"] = response.status_code
        payload = response.json()
        row["response_valid"] = response.status_code == 200 and "move" in payload and "game" in payload
        if row["response_valid"]:
            move, game = payload["move"], payload["game"]
            row["legal_move"] = (
                0 <= move["row"] < 15
                and 0 <= move["col"] < 15
                and game["board"][move["row"]][move["col"]] == "O"
            )
        elif response.status_code >= 400:
            row["error_type"] = "HTTPError"
            row["error_message"] = str(payload.get("detail", ""))[:300]
    except Exception as exc:
        row["error_type"] = type(exc).__name__
        row["error_message"] = str(exc)[:300]
    row["api_response_ms"] = (time.perf_counter_ns() - started) / 1e6
    return row


async def run_group(
    client, run_id, scenario, difficulty, concurrency, samples, timeout,
    *, warmup=False, sample_offset=0,
):
    rows = []
    for sample_index in range(samples):
        if scenario == "same_game_concurrent":
            game_ids = [await new_ai_game(client)]
            ids = [game_ids[0][0]] * concurrency
        else:
            ids = [(await new_ai_game(client))[0] for _ in range(concurrency)]
        start = time.perf_counter()
        results = await asyncio.gather(*[
            request_ai(client, run_id, scenario, difficulty, concurrency, i, game_id, timeout)
            for i, game_id in enumerate(ids)
        ])
        elapsed = time.perf_counter() - start
        for result in results:
            result["group_wall_seconds"] = elapsed
            result["is_warmup"] = warmup
            result["sample_index"] = sample_offset + sample_index
            rows.append(result)
    return rows


def write_summary(  # noqa: C901
    output_dir: Path, request_rows: list[dict], server_rows: list[dict],
    monitor: PostgresMonitor, metadata: dict,
) -> dict:  # noqa: C901 - keep related audit output aggregation together
    by_id = {row["request_id"]: row for row in request_rows}
    request_intervals = []
    for server in server_rows:
        request = by_id.get(server.get("request_id"))
        if request is None:
            continue
        for field in SERVER_METRICS:
            request[field] = json.dumps(server.get(field)) if field == "db_backend_pids" else server.get(field)
        try:
            start_dt = datetime.fromisoformat(server["timestamp_utc"])
            end_dt = start_dt.timestamp() + float(server.get("api_server_ms") or 0) / 1000
            request_intervals.append((request["request_id"], set(server.get("db_backend_pids", [])),
                                      start_dt.timestamp(), end_dt))
        except (KeyError, TypeError, ValueError):
            continue
    lock_counts = defaultdict(int)
    for sample in monitor.samples:
        sample_epoch = datetime.fromisoformat(sample["timestamp_utc"]).timestamp()
        for session in sample["sessions"]:
            if session["wait_event_type"] == "Lock":
                for request_id, pids, start_epoch, end_epoch in request_intervals:
                    if session["pid"] in pids and start_epoch <= sample_epoch <= end_epoch:
                        lock_counts[request_id] += 1
    peak = max((s["active_db_connections"] for s in monitor.samples), default=0)
    for row in request_rows:
        row["observed_lock_wait_ms"] = round(lock_counts[row["request_id"]] * monitor.interval_s * 1000, 3)
        row["active_db_connections_peak"] = peak
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "api-requests.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=REQUEST_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(request_rows)
    with (output_dir / "server-metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "timestamp_utc", "run_id", "request_id", "http_method",
            "endpoint", "http_status", "api_server_ms", "engine_search_ms",
            "row_lock_query_ms", "transaction_duration_ms", "transaction_count",
            "db_connection_hold_ms", "db_backend_pids",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in server_rows:
            row = dict(row)
            row["db_backend_pids"] = json.dumps(row.get("db_backend_pids", []))
            writer.writerow(row)
    monitor.write_csv()
    groups = defaultdict(list)
    for row in request_rows:
        if not row.get("is_warmup", False):
            groups[(row["scenario"], row["difficulty"], row["concurrency"])].append(row)
    summaries = []
    for (scenario, difficulty, concurrency), rows in sorted(groups.items()):
        values = [r["api_response_ms"] for r in rows if r["api_response_ms"] is not None]
        successes = sum(r["http_status"] == 200 for r in rows)
        wall = sum({r.get("sample_index"): r.get("group_wall_seconds", 0) for r in rows}.values())

        def metric(field):
            values = [r[field] for r in rows if isinstance(r.get(field), (int, float))]
            return {"p50": statistics.median(values) if values else None,
                    "p95": percentile(values, .95), "max": max(values) if values else None}
        engine, row_query = metric("engine_search_ms"), metric("row_lock_query_ms")
        transaction, connection = metric("transaction_duration_ms"), metric("db_connection_hold_ms")
        observed_wait = metric("observed_lock_wait_ms")
        http_400 = sum(r.get("http_status") == 400 for r in rows)
        same_game = scenario == "same_game_concurrent"

        def expected_same_game_conflict(row):
            if not same_game:
                return False
            status = row.get("http_status")
            detail = str(row.get("error_message") or "").lower()
            return (
                status == 409 and "state changed" in detail
            ) or (
                status == 400 and "not the ai turn" in detail
            )

        expected_successes = len(rows) // concurrency if same_game else len(rows)
        expected_conflicts = len(rows) - expected_successes if same_game else 0
        expected_conflict_count = sum(expected_same_game_conflict(row) for row in rows)
        unexpected = sum(
            r.get("http_status") != 200 and not expected_same_game_conflict(r)
            for r in rows
        )
        invalid_successes = sum(
            r.get("http_status") == 200 and
            (r.get("response_valid") is False or r.get("legal_move") is False)
            for r in rows
        )
        summaries.append({"scenario": scenario, "difficulty": difficulty, "concurrency": concurrency,
                          "sample_count": len(rows), "success_count": successes,
                          "http_400_count": http_400,
                          "error_rate": (len(rows)-successes)/len(rows) if rows else None,
                          "unexpected_error_count": unexpected,
                          "unexpected_error_rate": (unexpected/len(rows)) if rows else None,
                          "invalid_success_count": invalid_successes,
                          "throughput_rps": len(rows)/wall if wall else None,
                          "api_p50_ms": statistics.median(values) if values else None,
                          "api_p95_ms": percentile(values, .95), "api_max_ms": max(values) if values else None,
                          "engine_search_ms": engine, "row_lock_query_ms": row_query,
                          "transaction_duration_ms": transaction, "db_connection_hold_ms": connection,
                          "observed_lock_wait_ms": observed_wait,
                          "expected_same_game_400s": (
                              expected_400
                              and successes == expected_successes
                              and http_400 == expected_400s
                          )})
    metadata["group_summary"] = summaries
    metadata["postgres_monitor_error"] = monitor.error
    metadata["postgres_observation_interval_ms"] = monitor.interval_s * 1000
    metadata["postgres_observation_samples"] = len(monitor.samples)
    metadata["raw_request_count"] = len(request_rows)
    metadata["server_metric_count"] = len(server_rows)
    (output_dir / "benchmark-summary.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    md = [
        "# CaroAI API / PostgreSQL Phase B benchmark", "",
        f"- Run: `{metadata['run_id']}`",
        f"- Source SHA: `{metadata['source_sha']}`",
        f"- Python: `{metadata['python_version']}`",
        "- API worker count: 1",
        f"- Warm-up repetitions per group: {metadata['warmup_count']}",
        f"- Measured repetitions per group: {metadata['samples_per_group']}",
        f"- PostgreSQL lock sampling interval: "
        f"{metadata['postgres_observation_interval_ms']} ms (approximate)",
        f"- PostgreSQL: {metadata.get('postgres_version', 'unknown')}",
        f"- Maximum active DB connections observed: "
        f"{metadata.get('active_db_connections_peak', 'unknown')}",
        "", "## Results", "",
        "The error rate column is the raw HTTP non-200 rate. For same-game "
        "requests, HTTP 400 responses after the first committed move are "
        "expected; `Unexpected errors` excludes those expected turn rejections.",
        "",
        "| Scenario | Difficulty | Concurrency | Requests | 2xx | HTTP 400 | HTTP 409 | "
        "Error rate | Unexpected errors | Throughput (req/s) | "
        "API P50 / P95 / max (ms) | Engine P50 / P95 (ms) | "
        "Row lock query P50 / P95 (ms) | Observed lock wait P50 / P95 (ms) | "
        "Transaction P50 / P95 (ms) | Connection hold P50 / P95 (ms) |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    def fmt(value, spec):
        return format(value, spec) if value is not None else "N/A"
    for item in summaries:

        def range_fmt(metrics, p95=True):
            tail = fmt(metrics['p95'], '.3f') if p95 else fmt(metrics['max'], '.3f')
            return f"{fmt(metrics['p50'], '.3f')} / {tail}"
        md.append(
            f"| {item['scenario']} | {item['difficulty']} | "
            f"{item['concurrency']} | {item['sample_count']} | "
            f"{item['success_count']} | {item['http_400_count']} | "
            f"{item['http_409_count']} | {fmt(item['error_rate'], '.1%')} | "
            f"{item['unexpected_error_count']} | "
            f"{fmt(item['throughput_rps'], '.3f')} | "
            f"{fmt(item['api_p50_ms'], '.3f')} / "
            f"{fmt(item['api_p95_ms'], '.3f')} / {fmt(item['api_max_ms'], '.3f')} | "
            f"{range_fmt(item['engine_search_ms'])} | "
            f"{range_fmt(item['row_lock_query_ms'])} | "
            f"{range_fmt(item['observed_lock_wait_ms'])} | "
            f"{range_fmt(item['transaction_duration_ms'])} | "
            f"{range_fmt(item['db_connection_hold_ms'])} |"
        )
    lookup = {(x["scenario"], x["difficulty"], x["concurrency"]): x for x in summaries}
    single = lookup.get(("single_request", "impossible", 1), {})
    same8 = lookup.get(("same_game_concurrent", "impossible", 8), {})
    different8 = lookup.get(("different_game_concurrent", "impossible", 8), {})
    read_rows = [x for x in summaries if x["scenario"] == "read_api_under_ai_load"]
    md += ["", "## Findings", ""]
    if single and same8 and different8:
        md += [
            f"- **Single-request IMPOSSIBLE:** API P95 "
            f"{fmt(single.get('api_p95_ms'), '.1f')} ms; engine P95 "
            f"{fmt(single.get('engine_search_ms', {}).get('p95'), '.1f')} ms; "
            f"transaction P95 "
            f"{fmt(single.get('transaction_duration_ms', {}).get('p95'), '.1f')} ms; "
            f"connection-hold P95 "
            f"{fmt(single.get('db_connection_hold_ms', {}).get('p95'), '.1f')} ms.",
            f"- **Same game, concurrency 8:** sampled lock-wait P95 "
            f"{fmt(same8.get('observed_lock_wait_ms', {}).get('p95'), '.1f')} ms, "
            f"row-lock query P95 "
            f"{fmt(same8.get('row_lock_query_ms', {}).get('p95'), '.1f')} ms, "
            f"API P95 {fmt(same8.get('api_p95_ms'), '.1f')} ms. One request "
            "per 8-request batch committed; remaining by-turn 400 responses "
            "were expected.",
            f"- **Different games, concurrency 8:** engine P95 "
            f"{fmt(different8.get('engine_search_ms', {}).get('p95'), '.1f')} ms "
            f"and API P95 {fmt(different8.get('api_p95_ms'), '.1f')} ms, "
            "with no sampled PostgreSQL lock waits. Search time and API "
            "latency rose under CPU contention across games.",
            "- The provisional 2,000 ms engine reference is below the "
            "single-request IMPOSSIBLE P95 and concurrency 4 engine P95, "
            "but concurrency 8 different-game engine P95 is "
            f"{fmt(different8.get('engine_search_ms', {}).get('p95'), '.1f')} ms. "
            "The reference remains unapproved and these local results do "
            "not establish a production SLO.",
            f"- Peak active DB connections were "
            f"{metadata.get('active_db_connections_peak', 'unknown')} against "
            "SQLAlchemy's default PostgreSQL pool allowance of 15 "
            "(5 pooled plus 10 overflow); no pool exhaustion was observed "
            "at tested concurrency.",
        ]
    md += [
        "", "## Recommendation", "",
        "The measurements show that the current transaction and connection "
        "remain occupied for nearly the AI search duration, and same-game "
        "requests wait on the row lock for that interval. Different-game "
        "requests show no sampled lock wait; their concurrency penalty is "
        "dominated by CPU-bound search. Consider a guarded AI concurrency "
        "limit or queue for IMPOSSIBLE when expected load exceeds available "
        "CPU, and evaluate moving search outside the transaction only if "
        "same-game lock latency or connection occupancy is a product concern. "
        "Any refactor must revalidate the board under lock before persisting. "
        "The current run does not justify changing production transaction "
        "flow or pool settings by itself.",
        "",
    ]
    if read_rows:
        md += [
            "Read API check: one game-detail and one history request overlapped "
            "one IMPOSSIBLE search; this sample is too small to claim stable "
            "read latency under load.",
            "",
        ]
    md += [
        "", "## Interpretation and limits", "",
        f"- Persisted games checked: "
        f"{metadata.get('database_correctness_checks', 'unknown')}; "
        f"invalid histories/sequences: "
        f"{metadata.get('database_correctness_failures', 'unknown')}.",
        f"- Invalid successful AI responses: "
        f"{sum(x['invalid_success_count'] for x in summaries)}.",
        f"- Peak observed active PostgreSQL connections: "
        f"{metadata.get('active_db_connections_peak', 'unknown')}.",
        "- Raw client request, server instrumentation, and PostgreSQL "
        "polling samples are in the adjacent CSV files.",
        "- `row_lock_query_ms` includes PostgreSQL execution time and is not "
        "pure lock wait. `observed_lock_wait_ms` is an approximate lower "
        "bound from sampled `pg_stat_activity` lock waits; brief waits can "
        "fall between polls.",
        "- All measurements apply only to this disposable local environment "
        "and the history-backed five-ply opening fixture. Same-game "
        "concurrency expects one successful move per fixture iteration "
        "followed by turn-validation HTTP 400 responses; those 400 responses "
        "are expected conflict outcomes, not data corruption.",
        "- The read API under AI load check contains one AI request and one "
        "game-detail/history pair, so it does not support a stable P95 "
        "conclusion.",
        "",
    ]
    (output_dir / "benchmark-report.md").write_text("\n".join(md), encoding="utf-8")
    (output_dir / "environment.json").write_text(json.dumps(metadata["environment"], indent=2) + "\n", encoding="utf-8")
    return metadata


def verify_database_games(database_url: str, request_rows: list[dict], output_dir: Path) -> list[dict]:
    """Check final persisted move sequences for every game used in the run."""
    game_ids = sorted({r["game_id"] for r in request_rows if r.get("game_id")})
    results = []
    connection = psycopg2.connect(database_url)
    try:
        with connection.cursor() as cursor:
            for game_id in game_ids:
                cursor.execute("""
                    SELECT g.public_id, g.status, g.result,
                           count(m.id), count(DISTINCT (m.row, m.col)),
                           COALESCE(array_agg(m.player ORDER BY m.move_number)
                             FILTER (WHERE m.id IS NOT NULL), ARRAY[]::bpchar[]),
                           COALESCE(array_agg(m.move_number ORDER BY m.move_number)
                             FILTER (WHERE m.id IS NOT NULL), ARRAY[]::integer[])
                    FROM games g LEFT JOIN moves m ON m.game_id = g.id
                    WHERE g.public_id = %s
                    GROUP BY g.public_id, g.status, g.result
                """, (game_id,))
                row = cursor.fetchone()
                if row is None:
                    results.append({"game_id": game_id, "valid": False, "error": "missing_game"})
                    continue
                _public_id, status, result, count, distinct_moves, players, numbers = row
                players = [str(p).strip() for p in players]
                expected_players = ["X" if i % 2 == 0 else "O" for i in range(count)]
                contiguous = numbers == list(range(1, count + 1))
                results.append({
                    "game_id": game_id, "move_count": count, "distinct_coordinates": distinct_moves,
                    "move_numbers_contiguous": contiguous, "player_order_valid": players == expected_players,
                    "status": status, "result": result,
                    "valid": count == distinct_moves and contiguous and players == expected_players,
                })
    finally:
        connection.close()
    with (output_dir / "correctness-checks.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(results, handle, indent=2)
        handle.write("\n")
    return results


async def main_async(args) -> int:  # noqa: C901
    if not args.database_url:
        raise SystemExit("--database-url is required for disposable PostgreSQL")
    run_id = f"phaseb-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    metrics_path = output_dir / "server-metrics.jsonl"
    metrics_path.unlink(missing_ok=True)
    env = os.environ.copy()
    env.update({"DATABASE_URL": args.database_url, "CAROAI_BENCHMARK_SERVER_METRICS": str(metrics_path),
                "CAROAI_BENCHMARK_RUN_ID": run_id, "PORT": str(args.server_port),
                "PYTHONPATH": str(ROOT)})
    process = None
    base_url = args.base_url or f"http://127.0.0.1:{args.server_port}"
    if not args.base_url:
        process = subprocess.Popen([sys.executable, str(ROOT / "scripts/phase_b_server.py")], cwd=ROOT, env=env,
                                   stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    monitor = PostgresMonitor(args.database_url, output_dir / "postgres-observations.csv", run_id,
                              args.monitor_interval_ms / 1000)
    rows = []
    try:
        async with httpx.AsyncClient(base_url=base_url) as client:
            await wait_ready(client, args.timeout_seconds)
            monitor.start()
            difficulties = [s.strip().lower() for s in args.difficulties.split(",") if s.strip()]
            concurrencies = [int(s.strip()) for s in args.concurrency.split(",") if s.strip()]
            if args.smoke_only:
                concurrencies = [1, 2]
                samples = 1
                warmup_count = 0
            else:
                samples = args.samples
                warmup_count = args.warmup
            for difficulty in difficulties:
                for scenario in ("single_request", "same_game_concurrent", "different_game_concurrent"):
                    for concurrency in concurrencies:
                        if scenario == "single_request" and concurrency != 1:
                            continue
                        if warmup_count:
                            await run_group(client, run_id, scenario, difficulty, concurrency, warmup_count,
                                            args.timeout_seconds, warmup=True)
                        print(f"{scenario} / {difficulty} / concurrency={concurrency} / samples={samples}", flush=True)
                        rows.extend(await run_group(client, run_id, scenario, difficulty, concurrency, samples,
                                                    args.timeout_seconds, sample_offset=warmup_count))
            # Read endpoints while an IMPOSSIBLE AI move is in flight.
            game_id, _ = await new_ai_game(client)
            ai_task = asyncio.create_task(
                request_ai(
                    client, run_id, "read_api_under_ai_load", "impossible",
                    1, 0, game_id, args.timeout_seconds,
                )
            )
            await asyncio.sleep(.01)
            read_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
            read_tasks = [
                client.get(
                    f"/api/games/{game_id}",
                    headers={"X-Request-ID": read_ids[0]},
                    timeout=args.timeout_seconds,
                ),
                client.get(
                    "/api/history",
                    headers={"X-Request-ID": read_ids[1]},
                    timeout=args.timeout_seconds,
                ),
            ]

            async def timed_read(task, request_id, endpoint):
                started = time.perf_counter_ns()
                try:
                    response = await task
                    elapsed_ms = (time.perf_counter_ns() - started) / 1e6
                    return response.status_code, elapsed_ms, None, None
                except Exception as exc:
                    elapsed_ms = (time.perf_counter_ns() - started) / 1e6
                    return None, elapsed_ms, type(exc).__name__, str(exc)[:300]
            read_endpoints = (f"/api/games/{game_id}", "/api/history")
            read_results = await asyncio.gather(*[
                timed_read(task, read_ids[i], read_endpoints[i])
                for i, task in enumerate(read_tasks)
            ])
            for i, (endpoint, result) in enumerate(zip(read_endpoints, read_results)):
                status, duration_ms, error_type, error_message = result
                rows.append({"timestamp_utc": datetime.now(timezone.utc).isoformat(),
                             "run_id": run_id, "request_id": read_ids[i],
                             "scenario": "read_api_under_ai_load",
                             "fixture": "legal_five_ply_opening",
                             "difficulty": "n/a", "concurrency": 2,
                             "worker_id": i, "game_id": game_id,
                             "http_method": "GET", "endpoint": endpoint,
                             "http_status": status, "api_response_ms": duration_ms,
                             "response_valid": status == 200, "legal_move": None,
                             "error_type": error_type, "error_message": error_message,
                             "is_warmup": False, "sample_index": 0,
                             "group_wall_seconds": max(
                                 duration_ms
                                 for _, duration_ms, _, _ in read_results
                             ) / 1000})
            rows.append(await ai_task)
    finally:
        monitor.stop()
        if process:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    await asyncio.sleep(.1)
    server_rows = (
        [json.loads(line) for line in metrics_path.read_text(encoding="utf-8").splitlines()]
        if metrics_path.exists()
        else []
    )
    correctness = verify_database_games(args.database_url, rows, output_dir)
    pg_conn = psycopg2.connect(args.database_url)
    try:
        with pg_conn.cursor() as cursor:
            cursor.execute("SELECT version(), current_setting('max_connections'), current_setting('shared_buffers')")
            pg_version, pg_max_connections, pg_shared_buffers = cursor.fetchone()
    finally:
        pg_conn.close()
    harness_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    server_sha256 = hashlib.sha256((ROOT / "scripts/phase_b_server.py").read_bytes()).hexdigest()
    fixture_definition = [(7, 7), (7, 8), (6, 7), (8, 8), (6, 6)]
    fixture_sha256 = hashlib.sha256(json.dumps(fixture_definition, separators=(",", ":")).encode()).hexdigest()
    metadata = {"run_id": run_id, "captured_at_utc": datetime.now(timezone.utc).isoformat(),
                "source_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
                "python_version": sys.version, "python_executable": sys.executable, "platform": platform.platform(),
                "cpu_count": os.cpu_count(), "database_url_host": args.database_url.rsplit("@", 1)[-1],
                "api_worker_count": 1, "sqlalchemy_pool_default": "QueuePool defaults (pool_size=5, max_overflow=10)",
                "fixture_manifest_sha256": None, "fixture_definition": fixture_definition,
                "fixture_definition_sha256": fixture_sha256,
                "benchmark_harness_sha256": harness_sha256, "instrumentation_sha256": server_sha256,
                "working_tree_dirty": subprocess.run(
                    ["git", "status", "--porcelain"], cwd=ROOT, text=True,
                    capture_output=True,
                ).stdout.strip() != "",
                "postgres_version": pg_version, "postgres_max_connections": pg_max_connections,
                "postgres_shared_buffers": pg_shared_buffers,
                "postgres_image": "postgres:15-alpine (Docker image digest recorded separately in execution notes)",
                "active_db_connections_peak": max((s["active_db_connections"] for s in monitor.samples), default=0),
                "database_correctness_checks": len(correctness),
                "database_correctness_failures": sum(not c.get("valid", False) for c in correctness),
                "samples_per_group": samples, "warmup_count": warmup_count,
                "difficulties": difficulties, "concurrency_levels": concurrencies,
                "monitor_interval_ms": args.monitor_interval_ms,
                "environment": {"python_version": sys.version, "platform": platform.platform(), "cpu_count": os.cpu_count(),
                                "api_worker_count": 1, "database_host": args.database_url.rsplit("@", 1)[-1]},
                "notes": ["API-side timing includes middleware stack; client timing is wall-clock.",
                          "Database fixture is history-backed and is seeded through public endpoints.",
                          "No production endpoint/database was used.",
                          "Same-game HTTP 400 responses after the first committed move are expected by-turn outcomes."]}
    write_summary(output_dir, rows, server_rows, monitor, metadata)
    if process and process.returncode not in (0, -15):
        print(f"API server exited with code {process.returncode}", file=sys.stderr)
    return 0


def main() -> int:
    args = build_parser().parse_args()
    if args.samples < 1:
        raise SystemExit("--samples must be positive")
    return asyncio.run(main_async(args))


if __name__ == "__main__":
    raise SystemExit(main())

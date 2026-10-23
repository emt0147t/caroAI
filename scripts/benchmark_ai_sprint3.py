"""Reproducible Sprint 3 AI benchmark: raw trials, median/p95, SHA and environment."""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import os
import platform
import random
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ai.engine import DIFFICULTY_CONFIG, get_ai_move
from app.ai.evaluator import BOARD_SIZE, EMPTY, check_win_at, has_five_in_a_row
from app.ai.move_generator import get_candidate_moves

REPORTS_DIR = ROOT / "reports"
FIXTURE_COUNT_MINIMUM = 10
PROPOSED_SLO_MS = 2_000
PLAYERS = (1, 2)
CSV_FIELDS = [
    "timestamp_utc",
    "source_sha",
    "environment_id",
    "fixture",
    "category",
    "occupied_stones",
    "difficulty",
    "depth",
    "candidate_limit",
    "root_candidate_count",
    "trial",
    "is_warmup",
    "elapsed_ms",
    "chosen_row",
    "chosen_col",
    "score",
    "output_shape_valid",
    "legal_move",
    "board_unchanged",
    "expected_move_ok",
    "error_type",
    "error",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def empty_board() -> list[list[int]]:
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def board_from_stones(stones: list[dict[str, int]]) -> list[list[int]]:
    board = empty_board()
    seen: set[tuple[int, int]] = set()
    for stone in stones:
        row, col, player = stone["row"], stone["col"], stone["player"]
        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            raise ValueError(f"Stone outside board: {(row, col)}")
        if player not in PLAYERS:
            raise ValueError(f"Unsupported player value: {player}")
        if (row, col) in seen:
            raise ValueError(f"Duplicate stone coordinate: {(row, col)}")
        seen.add((row, col))
        board[row][col] = player
    return board


def load_demo_fixtures() -> list[dict[str, Any]]:
    manifest_path = REPORTS_DIR / "ai-demo-boards.json"
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    if manifest.get("board_size") != BOARD_SIZE:
        raise ValueError("Demo manifest board_size does not match AI engine")
    fixtures = []
    for item in manifest["fixtures"]:
        fixtures.append({
            "name": item["name"],
            "category": item["category"],
            "description": item["description"],
            "ai_player": int(item["ai_player"]),
            "board": board_from_stones(item["stones"]),
            "occupied_stones": len(item["stones"]),
            "expected_moves": [tuple(move) for move in item.get("expected_moves", [])],
            "is_demo": True,
            "require_no_immediate_win": bool(item.get("require_no_immediate_win", False)),
            "difficulty": item.get("difficulty", ["EASY", "MEDIUM", "HARD"]),
        })
    return fixtures


DENSE_MIDGAME_34_CELLS = [
    (2, 6, 1),
    (3, 9, 1),
    (4, 6, 2),
    (4, 9, 2),
    (4, 11, 2),
    (4, 12, 1),
    (5, 6, 2),
    (5, 9, 1),
    (6, 2, 1),
    (6, 6, 1),
    (6, 9, 1),
    (7, 2, 2),
    (7, 4, 2),
    (7, 5, 2),
    (7, 9, 2),
    (7, 11, 2),
    (8, 2, 1),
    (8, 5, 1),
    (8, 8, 1),
    (8, 10, 1),
    (9, 6, 1),
    (9, 7, 1),
    (9, 8, 2),
    (10, 2, 1),
    (10, 3, 2),
    (10, 5, 2),
    (10, 12, 1),
    (11, 2, 2),
    (11, 5, 2),
    (11, 7, 2),
    (11, 9, 2),
    (12, 3, 2),
    (12, 4, 1),
    (12, 9, 1),
]

DENSE_MIDGAME_42_CELLS = [
    (2, 8, 2),
    (3, 2, 1),
    (3, 5, 2),
    (3, 6, 2),
    (3, 7, 2),
    (3, 11, 2),
    (4, 2, 1),
    (4, 8, 1),
    (4, 10, 1),
    (4, 12, 2),
    (5, 3, 2),
    (5, 6, 1),
    (5, 7, 1),
    (5, 8, 2),
    (5, 11, 1),
    (6, 2, 1),
    (6, 5, 1),
    (6, 6, 2),
    (6, 10, 2),
    (7, 2, 1),
    (7, 3, 2),
    (7, 4, 1),
    (7, 5, 1),
    (7, 10, 2),
    (8, 2, 1),
    (8, 3, 2),
    (8, 5, 2),
    (8, 6, 1),
    (9, 2, 2),
    (9, 3, 2),
    (9, 4, 1),
    (9, 6, 1),
    (10, 7, 1),
    (10, 8, 2),
    (11, 3, 1),
    (11, 5, 2),
    (11, 9, 2),
    (11, 11, 1),
    (12, 2, 2),
    (12, 3, 2),
    (12, 8, 1),
    (12, 9, 1),
]


def fixture_from_cells(
    name: str,
    category: str,
    cells: list[tuple[int, int, int]],
    description: str,
    ai_player: int = 1,
) -> dict[str, Any]:
    board = empty_board()
    for row, col, player in cells:
        if board[row][col] != EMPTY:
            raise ValueError(f"Duplicate coordinate in fixture {name}: {(row, col)}")
        board[row][col] = player
    return {
        "name": name,
        "category": category,
        "description": description,
        "ai_player": ai_player,
        "board": board,
        "occupied_stones": len(cells),
        "expected_moves": [],
        "is_demo": False,
        "require_no_immediate_win": False,
        "difficulty": ["EASY", "MEDIUM", "HARD"],
    }


def build_fixtures() -> list[dict[str, Any]]:
    fixtures = load_demo_fixtures()
    fixtures.extend([
        fixture_from_cells(
            "opening_two_stones", "opening",
            [(7, 7, 1), (7, 8, 2)],
            "Two-stone opening around the center.",
        ),
        fixture_from_cells(
            "opening_six_stones", "opening",
            [(7, 7, 1), (7, 8, 2), (6, 7, 1),
             (8, 8, 2), (6, 6, 1), (8, 7, 2)],
            "Six stones spread across the central opening.",
        ),
        fixture_from_cells(
            "mid_game_spread", "midgame",
            [(2, 2, 1), (2, 3, 2), (3, 2, 1), (4, 5, 2),
             (5, 6, 1), (6, 5, 2), (8, 8, 1), (8, 9, 2),
             (9, 8, 1), (10, 11, 2), (11, 10, 1), (12, 12, 2)],
            "Twelve stones distributed across separated local groups.",
        ),
        fixture_from_cells(
            "edge_midgame", "edge",
            [(0, 0, 1), (0, 1, 2), (1, 0, 1), (2, 2, 2),
             (3, 1, 1), (3, 2, 2), (5, 5, 1), (5, 6, 2),
             (6, 5, 1), (8, 9, 2), (9, 9, 1), (10, 8, 2)],
            "Mixed edge and center activity without an existing five.",
        ),
        fixture_from_cells(
            "competing_open_threes", "tactical_midgame",
            [(6, 4, 1), (6, 5, 1), (6, 6, 1),
             (4, 9, 2), (5, 9, 2), (6, 9, 2),
             (8, 4, 1), (8, 9, 2), (10, 3, 1), (10, 10, 2)],
            "Competing three-stone patterns from both players.",
        ),
        fixture_from_cells(
            "complex_mid_game", "forced_block",
            [(5, 5, 1), (5, 6, 2), (6, 5, 2), (6, 6, 1),
             (6, 7, 1), (5, 7, 2), (7, 6, 1), (7, 7, 2),
             (8, 7, 1), (8, 8, 2), (7, 8, 2), (8, 6, 1),
             (9, 7, 1), (9, 8, 2), (7, 5, 1), (6, 8, 2)],
            "Legacy complex fixture containing an opponent four-in-a-row threat.",
        ),
    ])
    fixtures.append(fixture_from_cells(
        "dense_midgame_34_stones", "dense_midgame", DENSE_MIDGAME_34_CELLS,
        "Fixed, reviewed 34-stone nonterminal board (was initially generated from seed 17).",
    ))
    fixtures.append(fixture_from_cells(
        "dense_midgame_42_stones", "dense_midgame", DENSE_MIDGAME_42_CELLS,
        "Fixed, reviewed 42-stone nonterminal board (was initially generated from seed 29).",
    ))
    validate_fixtures(fixtures)
    return fixtures


def has_immediate_win(board: list[list[int]], player: int) -> bool:
    for row, col in get_candidate_moves(board, radius=2):
        board[row][col] = player
        try:
            if check_win_at(board, row, col, player):
                return True
        finally:
            board[row][col] = EMPTY
    return False


def validate_fixtures(fixtures: list[dict[str, Any]]) -> None:
    if len(fixtures) < FIXTURE_COUNT_MINIMUM:
        raise ValueError(
            f"Sprint 3 benchmark needs at least {FIXTURE_COUNT_MINIMUM} fixtures; "
            f"found {len(fixtures)}"
        )
    names = [fixture["name"] for fixture in fixtures]
    if len(names) != len(set(names)):
        raise ValueError("Benchmark fixture names must be unique")
    for fixture in fixtures:
        board = fixture["board"]
        if len(board) != BOARD_SIZE or any(len(row) != BOARD_SIZE for row in board):
            raise ValueError(f"Fixture {fixture['name']} is not a 15x15 board")
        if any(cell not in (EMPTY, 1, 2) for row in board for cell in row):
            raise ValueError(f"Fixture {fixture['name']} has an invalid cell value")
        for player in PLAYERS:
            if has_five_in_a_row(board, player):
                raise ValueError(
                    f"Fixture {fixture['name']} is already terminal for player {player}"
                )
        if fixture["require_no_immediate_win"]:
            opponent = 2 if fixture["ai_player"] == 1 else 1
            if has_immediate_win(board, fixture["ai_player"]) or has_immediate_win(board, opponent):
                raise ValueError(
                    f"Fixture {fixture['name']} must not have an immediate win for either player"
                )


def validate_full_sha(value: str) -> str:
    """Validate a full 40-hex-character Git SHA without shortening it."""
    sha = value.strip().lower()
    if len(sha) != 40 or any(ch not in "0123456789abcdef" for ch in sha):
        raise ValueError(f"Expected a full 40-character Git SHA, got: {value!r}")
    return sha


def get_source_sha(explicit_sha: str | None = None) -> tuple[str, str]:
    """
    Resolve a full source SHA. In a normal checkout, verify it against HEAD and
    require the measured source files to be clean. Minimal runtime images often
    omit .git; in that case require the caller to pass the full source SHA from
    the image/release metadata instead of guessing.
    """
    git_error = None
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        git_sha = validate_full_sha(result.stdout.strip())
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        git_error = exc
        git_sha = None

    if git_sha is None:
        if not explicit_sha:
            raise RuntimeError(
                "Git metadata is unavailable. Pass --source-sha with the full "
                "40-character SHA used to build this environment/image."
            ) from git_error
        return validate_full_sha(explicit_sha), "provided-no-git-metadata"

    if explicit_sha:
        provided_sha = validate_full_sha(explicit_sha)
        if provided_sha != git_sha:
            raise RuntimeError(
                f"--source-sha {provided_sha} does not match git HEAD {git_sha}"
            )

    # The SHA must identify the AI code, benchmark script, and exact demo fixtures.
    # Generated reports are intentionally excluded so the benchmark remains rerunnable.
    status = subprocess.run(
        [
            "git", "status", "--porcelain", "--",
            "app/ai", "scripts/benchmark_ai_sprint3.py",
            "reports/ai-demo-boards.json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if status:
        raise RuntimeError(
            "Benchmark source files are modified or untracked. Commit/sync the "
            "AI engine, benchmark script and demo manifest before measuring. "
            f"git status: {status}"
        )
    method = "provided-and-verified-against-git" if explicit_sha else "git-head"
    return git_sha, method


def cpu_name() -> str:
    value = platform.processor().strip()
    if value:
        return value
    if sys.platform.startswith("linux"):
        try:
            for line in Path("/proc/cpuinfo").read_text(encoding="utf-8").splitlines():
                if line.lower().startswith("model name"):
                    return line.split(":", 1)[1].strip()
        except OSError:
            pass
    if os.name == "nt":
        try:
            output = subprocess.check_output(
                ["wmic", "cpu", "get", "Name", "/value"],
                stderr=subprocess.DEVNULL,
                timeout=3,
                text=True,
            )
            for line in output.splitlines():
                if line.startswith("Name="):
                    return line.split("=", 1)[1].strip()
        except (OSError, subprocess.SubprocessError):
            pass
    return "unknown"


def collect_environment(source_sha: str, command: str, source_sha_method: str) -> dict[str, Any]:
    docker_markers = (
        Path("/.dockerenv").exists()
        or bool(os.environ.get("container"))
        or bool(os.environ.get("KUBERNETES_SERVICE_HOST"))
    )
    return {
        "captured_at_utc": utc_now(),
        "source_sha": source_sha,
        "source_sha_method": source_sha_method,
        "python_version": sys.version.replace("\n", " "),
        "python_executable": sys.executable,
        "argv": list(sys.argv),
        "platform": platform.platform(),
        "system": platform.system(),
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown",
        "cpu_name": cpu_name(),
        "is_container": bool(docker_markers),
        "container_hint": os.environ.get("container", "detected" if docker_markers else "not detected"),
        "command": command,
    }


def nearest_rank_percentile(values: list[float], percentile: float = 0.95) -> float | None:
    """Nearest-rank percentile; with five values p95 equals the maximum."""
    if not values:
        return None
    if not 0 < percentile <= 1:
        raise ValueError("percentile must be in (0, 1]")
    ordered = sorted(values)
    rank = math.ceil(percentile * len(ordered))
    return ordered[rank - 1]


def _valid_coordinate(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def run_trial(
    fixture: dict[str, Any],
    difficulty: str,
    trial: int,
    is_warmup: bool,
    source_sha: str,
    environment_id: str,
) -> dict[str, Any]:
    original = copy.deepcopy(fixture["board"])
    board_for_call = copy.deepcopy(original)
    config = DIFFICULTY_CONFIG[difficulty]
    root_candidate_count = len(get_candidate_moves(original, radius=2))
    start_ns = time.perf_counter_ns()
    result = None
    error_type = ""
    error_message = ""
    try:
        result = get_ai_move(
            board_for_call,
            ai_player=fixture["ai_player"],
            difficulty=difficulty,
        )
    except Exception as exc:  # Preserve the raw failure instead of hiding it.
        error_type = type(exc).__name__
        error_message = str(exc)
    elapsed_ms = (time.perf_counter_ns() - start_ns) / 1_000_000

    row = result.get("row") if isinstance(result, dict) else None
    col = result.get("col") if isinstance(result, dict) else None
    score = result.get("score") if isinstance(result, dict) else None
    has_expected_keys = (
        isinstance(result, dict)
        and all(key in result for key in ("row", "col", "score", "elapsed_ms"))
        and _valid_coordinate(row)
        and _valid_coordinate(col)
        and isinstance(score, int)
        and not isinstance(score, bool)
        and isinstance(result.get("elapsed_ms"), (int, float))
        and not isinstance(result.get("elapsed_ms"), bool)
        and result.get("elapsed_ms", -1) >= 0
    )
    in_bounds = (
        _valid_coordinate(row)
        and _valid_coordinate(col)
        and 0 <= row < BOARD_SIZE
        and 0 <= col < BOARD_SIZE
    )
    legal_move = bool(
        has_expected_keys
        and in_bounds
        and original[row][col] == EMPTY
    )
    board_unchanged = board_for_call == original
    expected_moves = fixture.get("expected_moves", [])
    expected_move_ok = None
    if expected_moves and has_expected_keys and in_bounds:
        expected_move_ok = [row, col] in expected_moves
    if not has_expected_keys and not error_type:
        error_type = "InvalidOutput"
        error_message = "AI output did not match the expected response contract"
    if has_expected_keys and not legal_move and not error_type:
        error_type = "IllegalMove"
        error_message = f"AI returned illegal move {(row, col)}"
    if not board_unchanged and not error_type:
        error_type = "BoardMutation"
        error_message = "AI mutated its input board"

    return {
        "timestamp_utc": utc_now(),
        "source_sha": source_sha,
        "environment_id": environment_id,
        "fixture": fixture["name"],
        "category": fixture["category"],
        "occupied_stones": fixture["occupied_stones"],
        "difficulty": difficulty,
        "depth": config["depth"],
        "candidate_limit": config["candidate_limit"],
        "root_candidate_count": root_candidate_count,
        "trial": trial,
        "is_warmup": is_warmup,
        "elapsed_ms": round(elapsed_ms, 6),
        "chosen_row": row,
        "chosen_col": col,
        "score": score,
        "output_shape_valid": bool(has_expected_keys),
        "legal_move": legal_move,
        "board_unchanged": board_unchanged,
        "expected_move_ok": expected_move_ok,
        "error_type": error_type,
        "error": error_message,
    }


def build_summaries(records: list[dict[str, Any]], fixtures: list[dict[str, Any]]) -> dict[str, Any]:
    measured = [row for row in records if not row["is_warmup"]]
    per_fixture = []
    for fixture in fixtures:
        for difficulty in DIFFICULTY_CONFIG:
            group = [
                row for row in measured
                if row["fixture"] == fixture["name"] and row["difficulty"] == difficulty
            ]
            elapsed = [float(row["elapsed_ms"]) for row in group if row["elapsed_ms"] is not None]
            failures = [
                row for row in group
                if row["error_type"]
                or not row["output_shape_valid"]
                or not row["legal_move"]
                or not row["board_unchanged"]
                or row["expected_move_ok"] is False
            ]
            per_fixture.append({
                "fixture": fixture["name"],
                "category": fixture["category"],
                "difficulty": difficulty,
                "sample_count": len(group),
                "successful_count": len(group) - len(failures),
                "failure_count": len(failures),
                "median_ms": statistics.median(elapsed) if elapsed else None,
                "p95_ms": nearest_rank_percentile(elapsed, 0.95),
                "min_ms": min(elapsed) if elapsed else None,
                "max_ms": max(elapsed) if elapsed else None,
            })

    per_difficulty = []
    for difficulty in DIFFICULTY_CONFIG:
        group = [
            row for row in measured
            if row["difficulty"] == difficulty and row["elapsed_ms"] is not None
        ]
        elapsed = [float(row["elapsed_ms"]) for row in group]
        failures = [
            row for row in measured
            if row["difficulty"] == difficulty
            and (
                row["error_type"]
                or not row["output_shape_valid"]
                or not row["legal_move"]
                or not row["board_unchanged"]
                or row["expected_move_ok"] is False
            )
        ]
        p95 = nearest_rank_percentile(elapsed, 0.95)
        per_difficulty.append({
            "difficulty": difficulty,
            "sample_count": len(elapsed),
            "failure_count": len(failures),
            "median_ms": statistics.median(elapsed) if elapsed else None,
            "p95_ms": p95,
            "min_ms": min(elapsed) if elapsed else None,
            "max_ms": max(elapsed) if elapsed else None,
            "proposed_slo_under_2000ms": p95 is not None and p95 <= PROPOSED_SLO_MS and not failures,
            "slo_acceptance": "PENDING_TEAM_CONFIRMATION",
        })
    return {"per_fixture_difficulty": per_fixture, "per_difficulty": per_difficulty}


def format_ms(value: Any) -> str:
    return "N/A" if value is None else f"{float(value):.3f}"


def render_report(
    environment: dict[str, Any],
    fixtures: list[dict[str, Any]],
    records: list[dict[str, Any]],
    summaries: dict[str, Any],
    runs: int,
    warmup: int,
    output_dir: Path,
) -> str:
    display_output_dir = os.path.relpath(output_dir, ROOT).replace("\\", "/")
    lines = [
        "# CaroAI Sprint 3 — AI Benchmark",
        "",
        f"- Generated at (UTC): {utc_now()}",
        f"- Full source SHA: {environment['source_sha']}",
        f"- Command: {environment['command']}",
        f"- Environment: Python {environment['python_version']}",
        f"- Platform: {environment['platform']}",
        f"- Machine: {environment['machine']}; CPU: {environment['cpu_name']}",
        f"- Container detected: {environment['is_container']} ({environment['container_hint']})",
        f"- Fixtures: {len(fixtures)}; difficulties: EASY/MEDIUM/HARD; warm-up: {warmup}; measured trials per fixture/difficulty: {runs}",
        "",
        "## Protocol and interpretation",
        "",
        "- Timing uses time.perf_counter_ns() around get_ai_move only. Board copying and root candidate-count collection occur outside the timed interval.",
        "- Raw CSV/JSON include measured trials and warm-up rows marked with is_warmup=true. Summaries exclude warm-ups.",
        "- The p95 uses the nearest-rank method: sorted sample at rank ceil(0.95 × n). For a fixture/difficulty with five trials, p95 equals that fixture's maximum and is not a high-confidence production percentile.",
        "- The by-difficulty p95 aggregates all fixture trials equally; it describes this explicit benchmark workload, not the real-world frequency distribution of player positions.",
        "- Root candidate count is measured before the timed call. Node count is not instrumented and is reported as N/A.",
        "- The proposed p95 ≤ 2,000 ms target is still pending explicit team confirmation. A measured value below the proposal is not, by itself, acceptance of the SLO.",
        "- If the runtime image omits .git, pass --source-sha from the exact image/release metadata; source_sha_method records whether Git HEAD was available and verified.",
        "",
        "## Environment metadata",
        "",
        "| Field | Value |",
        "|---|---|",
    ]
    for key, value in environment.items():
        lines.append(f"| {key} | {str(value).replace('|', '/')} |")

    lines.extend([
        "",
        "## Per-difficulty summary",
        "",
        "| Difficulty | Samples | Failures | Median (ms) | p95 (ms) | Min (ms) | Max (ms) | Proposed 2s threshold | SLO decision |",
        "|---|---:|---:|---:|---:|---:|---:|---|---|",
    ])
    for item in summaries["per_difficulty"]:
        lines.append(
            f"| {item['difficulty']} | {item['sample_count']} | {item['failure_count']} "
            f"| {format_ms(item['median_ms'])} | {format_ms(item['p95_ms'])} "
            f"| {format_ms(item['min_ms'])} | {format_ms(item['max_ms'])} "
            f"| {'BELOW PROPOSAL' if item['proposed_slo_under_2000ms'] else 'NOT MET / NO DATA'} "
            f"| {item['slo_acceptance']} |"
        )

    lines.extend([
        "",
        "## Per-fixture / difficulty results",
        "",
        "| Fixture | Category | Difficulty | n | Failures | Median (ms) | p95 (ms) | Min (ms) | Max (ms) |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ])
    for item in summaries["per_fixture_difficulty"]:
        lines.append(
            f"| {item['fixture']} | {item['category']} | {item['difficulty']} "
            f"| {item['sample_count']} | {item['failure_count']} "
            f"| {format_ms(item['median_ms'])} | {format_ms(item['p95_ms'])} "
            f"| {format_ms(item['min_ms'])} | {format_ms(item['max_ms'])} |"
        )

    demo_names = [fixture["name"] for fixture in fixtures if fixture["is_demo"]]
    lines.extend([
        "",
        "## Demo fixtures",
        "",
        "The exact coordinates and expected tactical outcomes are checked into reports/ai-demo-boards.json.",
        "",
    ])
    for name in demo_names:
        cases = [row for row in records if row["fixture"] == name and not row["is_warmup"]]
        measured_cases = len(cases)
        failed = sum(
            1 for row in cases
            if row["error_type"] or not row["legal_move"] or not row["board_unchanged"]
            or row["expected_move_ok"] is False
        )
        expected_results = [
            row["expected_move_ok"] for row in cases if row["expected_move_ok"] is not None
        ]
        expectation = "NOT APPLICABLE (generic midgame)" if not expected_results else (
            "PASS" if all(expected_results) else "FAIL"
        )
        lines.append(
            f"- {name}: {measured_cases} measured calls; failures={failed}; "
            f"expected tactical outcome={expectation}."
        )

    failures = sum(
        1 for row in records
        if not row["is_warmup"] and (
            row["error_type"] or not row["output_shape_valid"] or not row["legal_move"]
            or not row["board_unchanged"] or row["expected_move_ok"] is False
        )
    )
    lines.extend([
        "",
        "## Artifacts",
        "",
        f"- {display_output_dir}/ai-benchmark.csv — raw per-call measurements (including warm-ups flagged explicitly).",
        f"- {display_output_dir}/ai-benchmark.json — environment, configuration, raw rows and summaries.",
        "- reports/ai-demo-boards.json — fixed demo-board coordinates and expected tactical outcomes.",
        "",
        f"## Overall status: {'PASS (benchmark outputs legal and expected moves)' if failures == 0 else 'FAIL (inspect raw rows)'}",
        "",
        f"Measured trial failures: {failures}. This status only covers the listed fixtures, configurations and captured environment.",
        "",
    ])
    return "\n".join(lines)


def write_outputs(
    output_dir: Path,
    environment: dict[str, Any],
    fixtures: list[dict[str, Any]],
    records: list[dict[str, Any]],
    summaries: dict[str, Any],
    runs: int,
    warmup: int,
) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "ai-benchmark.csv"
    json_path = output_dir / "ai-benchmark.json"
    report_path = output_dir / "ai-benchmark.md"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    payload = {
        "schema_version": 1,
        "environment": environment,
        "config": DIFFICULTY_CONFIG,
        "fixture_count": len(fixtures),
        "difficulty_count": len(DIFFICULTY_CONFIG),
        "runs_per_fixture_difficulty": runs,
        "warmup_per_fixture_difficulty": warmup,
        "percentile_method": "nearest_rank",
        "proposed_slo_ms": PROPOSED_SLO_MS,
        "slo_acceptance": "PENDING_TEAM_CONFIRMATION",
        "node_count": "N/A (no node counter instrumented)",
        "fixtures": [
            {
                "name": item["name"],
                "category": item["category"],
                "description": item["description"],
                "ai_player": item["ai_player"],
                "occupied_stones": item["occupied_stones"],
                "expected_moves": [list(move) for move in item["expected_moves"]],
                "is_demo": item["is_demo"],
                "board": item["board"],
            }
            for item in fixtures
        ],
        "records": records,
        "summary": summaries,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(
        render_report(environment, fixtures, records, summaries, runs, warmup, output_dir),
        encoding="utf-8",
    )
    return csv_path, json_path, report_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=5, help="Measured trials per fixture/difficulty (minimum 5)")
    parser.add_argument("--warmup", type=int, default=1, help="Warm-up trials per fixture/difficulty (minimum 1)")
    parser.add_argument("--output-dir", type=Path, default=REPORTS_DIR, help="Directory for report and raw data")
    parser.add_argument(
        "--source-sha",
        default=os.environ.get("CAROAI_SOURCE_SHA"),
        help="Full 40-character source SHA for minimal images without .git; must match HEAD when Git metadata exists",
    )
    args = parser.parse_args()
    if args.runs < 5:
        parser.error("--runs must be at least 5 for the Sprint 3 protocol")
    if args.warmup < 1:
        parser.error("--warmup must be at least 1")
    if not args.output_dir.is_absolute():
        args.output_dir = ROOT / args.output_dir

    source_sha, source_sha_method = get_source_sha(args.source_sha)
    launcher = "py -3" if os.name == "nt" else "python3"
    command = (
        f"{launcher} scripts/benchmark_ai_sprint3.py --runs {args.runs} "
        f"--warmup {args.warmup}"
    )
    if args.source_sha:
        command += f" --source-sha {source_sha}"
    if args.output_dir != REPORTS_DIR:
        command += f' --output-dir "{args.output_dir}"'
    environment = collect_environment(source_sha, command, source_sha_method)
    environment_id = f"{platform.system().lower()}-{source_sha[:12]}"
    fixtures = build_fixtures()
    records: list[dict[str, Any]] = []

    print(
        f"Sprint 3 AI benchmark: {len(fixtures)} fixtures × "
        f"{len(DIFFICULTY_CONFIG)} difficulties × {args.runs} trials "
        f"plus {args.warmup} warm-up(s); SHA={source_sha}"
    )
    for fixture in fixtures:
        for difficulty in DIFFICULTY_CONFIG:
            for warmup_index in range(1, args.warmup + 1):
                record = run_trial(
                    fixture, difficulty, trial=warmup_index, is_warmup=True,
                    source_sha=source_sha, environment_id=environment_id,
                )
                record["trial"] = 0
                records.append(record)
            for trial in range(1, args.runs + 1):
                record = run_trial(
                    fixture, difficulty, trial=trial, is_warmup=False,
                    source_sha=source_sha, environment_id=environment_id,
                )
                records.append(record)
            recent = [
                row["elapsed_ms"] for row in records
                if row["fixture"] == fixture["name"]
                and row["difficulty"] == difficulty
                and not row["is_warmup"]
                and row["elapsed_ms"] is not None
            ]
            print(
                f"  {fixture['name']} / {difficulty}: "
                f"median={statistics.median(recent):.3f} ms" if recent
                else f"  {fixture['name']} / {difficulty}: no valid timing samples"
            )

    summaries = build_summaries(records, fixtures)
    outputs = write_outputs(
        args.output_dir, environment, fixtures, records, summaries, args.runs, args.warmup
    )
    print("Artifacts written:")
    for path in outputs:
        print(f"  {path}")

    failures = sum(
        1 for row in records
        if not row["is_warmup"] and (
            row["error_type"] or not row["output_shape_valid"] or not row["legal_move"]
            or not row["board_unchanged"] or row["expected_move_ok"] is False
        )
    )
    print(f"Measured trial failures: {failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

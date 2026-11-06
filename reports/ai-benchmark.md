# CaroAI AI Performance Baseline — Phase A & Phase B (2026-11-06)

**Scope:** four AI difficulty levels, controlled engine fixtures, and API/PostgreSQL contention measurements. This file's historical Phase 4 section follows below and must not be mistaken for the current four-difficulty baseline.

## Current source and reproducibility evidence

- Production source SHA: `42ee035ab42cd4c0bc934699f4d5433ff4b12a83`.
- Phase A benchmark workflow: [Run #4](https://github.com/emt0147t/caroAI/actions/runs/42237743095), source SHA `95c42e88c5eb9e88b719668345123b27df9eb2d6`, Ubuntu 24.04 / Python 3.11.18.
- Phase A raw artifact: 1,320 measured samples plus 132 warm-ups (11 fixtures × 4 difficulties × 30 measured + 3 warm-ups); archive SHA-256 `77d5f3c2e9624a6c5d65e9e633b1cf49ce6e9fca5b95c26ae5d5d4664aaa2ae0`.
- Phase B review: `phaseb-20261106T140340Z-980e7124`, Windows 10 / Python 3.11.9 / PostgreSQL 15.19 / one API worker / 10 ms PostgreSQL sampling. Review file: [PYTHON311-WINDOWS-REVIEW.md](benchmark-phase-b/PYTHON311-WINDOWS-REVIEW.md).

## Phase A — engine latency

Five of eleven fixtures trigger the root immediate-win/block shortcut and are not representative of depth-limited search. The six true search fixtures are `demo_midgame_search`, `opening_two_stones`, `opening_six_stones`, `mid_game_spread`, `edge_midgame`, and `dense_midgame_34_stones`.

| Difficulty | Search samples | Median ms | P95 ms | Max ms | Calls >2,000 ms |
|---|---:|---:|---:|---:|---:|
| EASY | 180 | 6.233 | 12.767 | 12.984 | 0 |
| MEDIUM | 180 | 29.246 | 61.734 | 65.278 | 0 |
| HARD | 180 | 235.822 | 523.455 | 527.765 | 0 |
| IMPOSSIBLE | 180 | 1,110.037 | 2,254.374 | 2,275.298 | 30 |

All 30 IMPOSSIBLE calls above 2,000 ms came from `mid_game_spread`: 12 separated stones and 109 root candidates; median 2,249.8 ms, P95 2,271.2 ms, maximum 2,275.3 ms. The dense 42-stone fixture unexpectedly has an immediate AI win and must be classified as a tactical shortcut, not a deep-search case.

The two-second reference remains provisional, not an adopted SLO. These equal-weight synthetic fixtures are not a production request distribution. Fixed win/block tests passing 30/30 at each difficulty demonstrates those particular tactics only, not optimal play.

## Phase B — API/PostgreSQL contention (IMPOSSIBLE)

| Scenario | Concurrency | Engine P95 ms | API P95 ms | Row-lock query P95 ms | Sampled lock wait P95 ms |
|---|---:|---:|---:|---:|---:|
| Single request | 1 | 728.4 | 739.9 | 1.3 | 0 |
| Different games | 2 | 1,493.9 | 1,565.7 | 1.6 | 0 |
| Different games | 4 | 2,827.9 | 3,263.6 | 150.8 | 0 |
| Different games | 8 | 5,329.8 | 6,311.7 | 329.7 | 0 |
| Same game | 2 | 1,053.5 | 1,070.6 | 970.4 | ~590 |
| Same game | 4 | 799.1 | 822.7 | 743.3 | ~440 |
| Same game | 8 | 855.3 | 888.9 | 624.2 | ~360 |

Different-game throughput stayed around 1.40–1.49 requests/second while API P95 increased to 6.31 seconds at concurrency 8 and no PostgreSQL lock wait was sampled. This is consistent with CPU-bound AI search contention in a one-worker process; it does not isolate Python GIL effects from CPU scheduling. Same-game requests waited on the row lock held through AI search. Sampled lock-wait figures are approximate lower bounds; row-lock query duration includes execution and lock wait, not pure lock time.

The Phase B run used one legal five-ply opening fixture, one API worker, and a 10 ms observer interval. It is a controlled local benchmark, not a Render production load test. Pool checkout wait was not directly instrumented in the run. The review also found the generated sentence claiming concurrency 4 was under the provisional two-second reference was wrong; the corrected table above shows engine P95 2,827.9 ms.

## Engineering implications

1. Add search instrumentation that separates node visits, candidate generation, candidate-cap pruning and alpha-beta pruning; occupied-stone count alone does not explain cost.
2. Evaluate a configurable time budget and a process-local admission guard for IMPOSSIBLE; keep them disabled or explicitly configured until the host-specific trade-off is measured.
3. Move Minimax computation outside the database row-lock transaction. Re-read under lock and compare the complete position/version before persisting; return a conflict rather than writing a stale move.
4. Extend fixture coverage to opening, midgame, tactical, edge and dense non-shortcut positions, and report each fixture rather than only aggregate means.

**Current evidence gaps:** Phase C metrics have not yet been collected; Render production AI latency per difficulty is not yet available; no formal latency SLO has been accepted.

---


# Historical CaroAI Phase 4 — M2 AI Regression and Benchmark Evidence

**Overall status: PARTIAL — Windows evidence and local regression validation complete; Linux/Docker evidence pending. M1 clarified that p95 ≤ 2,000 ms is a proposed performance target, not an adopted SLO.**

## 1. Source revisions

| Evidence | Full source SHA | Environment |
|---|---|---|
| Windows benchmark | `2b4e3c167d7ca0a2a5b530b7a251ced6dd37d526` | Windows 11, Python 3.13.14 |
| Phase 4 regression validation | `83a8c5f87209d84c0cb12beea02a12e20dd23357` | Windows 11, Python 3.13.14 |

The Phase 4 regression snapshot includes the merged benchmark fix and regression test. Comparing the Windows benchmark SHA with the Phase 4 develop SHA showed no changes to `app/ai/`, `scripts/benchmark_ai_sprint3.py`, `reports/ai-demo-boards.json`, or the AI unit-test files.

PR #36 was merged into `develop` in merge commit `914ba088a8753473c406f8870f6546ad44c38074`.

## 2. Windows benchmark

**Status: PASSED for the captured Windows workload.**

Reproduction command:

```powershell
py -3 scripts/benchmark_ai_sprint3.py --runs 5 --warmup 1 --output-dir reports/benchmark-windows-phase4-2b4e3c1
```

Protocol:
- 11 deterministic 15×15 fixtures.
- EASY, MEDIUM and HARD.
- 5 measured trials and 1 warm-up per fixture/difficulty.
- 198 raw records: 165 measured and 33 warm-up.
- 0 measured trial failures.

### Per-difficulty results

| Difficulty | Samples | Failures | Median (ms) | p95 (ms) |
|---|---:|---:|---:|---:|
| EASY | 55 | 0 | 2.1079 | 14.3417 |
| MEDIUM | 55 | 0 | 11.6002 | 61.5430 |
| HARD | 55 | 0 | 99.5755 | 973.8549 |

The p95 uses the nearest-rank method. Each difficulty aggregates 55 measured calls across 11 equally represented fixtures.

The aggregate p95 describes this benchmark workload, not the production distribution of player positions. Each per-fixture p95 has only five samples and equals that fixture's maximum; it is not a high-confidence production percentile.

### Difficulty configuration and observed midgame latency

The committed engine configuration and raw records show distinct search budgets:

| Difficulty | Depth | Candidate limit | Midgame demo median (ms) | Midgame demo p95 (ms) |
|---|---:|---:|---:|---:|
| EASY | 1 | 6 | 2.6847 | 4.7408 |
| MEDIUM | 2 | 10 | 11.6002 | 14.6660 |
| HARD | 3 | 14 | 99.5755 | 108.0097 |

The midgame figures are five measured trials for `demo_midgame_search`, not the 55-call aggregate above. All 15 measured calls (five per difficulty) returned the same legal coordinate `(6, 5)`. This demonstrates different configured search budgets and latency on this fixture; it does not prove that the selected move changes or that HARD is strategically optimal.

### Environment

- OS: Windows 11 (`Windows-11-10.0.26200-SP0`)
- Python: 3.13.14, 64-bit
- Machine: AMD64
- CPU identifier captured by the script: `Intel64 Family 6 Model 191 Stepping 2, GenuineIntel`
- Container: not detected

The captured CPU identifier is a platform string and does not establish a verified CPU SKU.

### Raw artifacts

- [Windows CSV — deliverable path](ai-benchmark.csv) — byte-for-byte copy of the environment-specific CSV.
- [Windows JSON — deliverable path](ai-benchmark.json) — byte-for-byte copy of the environment-specific JSON.
- [Windows environment CSV](benchmark-windows-phase4-2b4e3c1/ai-benchmark.csv)
- [Windows environment JSON](benchmark-windows-phase4-2b4e3c1/ai-benchmark.json)
- [Windows detailed report](benchmark-windows-phase4-2b4e3c1/ai-benchmark.md)
- [Demo board manifest](ai-demo-boards.json)

The root-level CSV/JSON are copies of this Windows run for the named M2 deliverable paths; the original environment-specific copies remain in their folder. They contain the same single Windows environment and do not combine measurements from different runtimes. Raw validation confirmed 198 rows, one full source SHA, timestamps, all 11 fixtures, all three difficulties, per-call latency, depth/candidate limit, output validity, legal-move, board-immutability, expected-move and error fields. All 165 measured records were legal, output-shape-valid and board-unchanged; there were zero errors and zero failed expected-move assertions.

## 3. Tactical demo-board outcomes

The three fixed demo positions are defined in `reports/ai-demo-boards.json`.

| Demo | Difficulty coverage | Measured calls | Outcome |
|---|---|---:|---|
| `demo_ai_win_now` | EASY/MEDIUM/HARD | 15 | Expected winning move `(7, 7)` passed |
| `demo_forced_block` | EASY/MEDIUM/HARD | 15 | Expected blocking move `(0, 1)` passed |
| `demo_midgame_search` | MEDIUM/HARD in regression tests; all difficulties in benchmark | 15 | Legal outputs; no fixed expected move |

The tactical meaning of the first two fixtures is explicit:

- **Win now:** X has four contiguous stones at row 7, columns 3–6; O occupies the left endpoint (7, 2). The only winning continuation is (7, 7), and the tests plus 15 measured calls confirm it.
- **Forced block:** O has four contiguous stones at row 0, columns 2–5; X occupies the right endpoint (0, 6). AI must block the remaining endpoint at (0, 1), confirmed by tests plus 15 measured calls.
- **Midgame:** the eight-stone central fixture has no existing five and no immediate win for either player. The benchmark emitted (6, 5) in all 15 measured calls, and all outputs were legal with the input board unchanged. There is no expected-move oracle for this fixture, so this is evidence of a legal search continuation, not proof that (6, 5) is the globally best strategic move.

**Evaluator/search limitations:** the evaluator scores line patterns (five, open/blocked four, open/blocked three and two) and minimax compares the incremental pattern totals as `AI score - 1.2 × opponent score`. Search is bounded to depth 1/2/3 by difficulty; candidates are generated within Chebyshev radius 2 of existing stones, ranked, then capped at 6/10/14. Alpha-beta pruning reduces the explored tree. These design choices make the result a bounded heuristic search, not exhaustive game-tree analysis or a proof of optimal play.

## 4. Phase 4 local regression validation

**Tested source SHA:** `83a8c5f87209d84c0cb12beea02a12e20dd23357`

Targeted AI tests:

```powershell
py -3 -m pytest tests/unit/test_ai_sprint3_benchmark.py tests/unit/test_ai_tactical.py tests/unit/test_ai_immutability.py tests/unit/test_ai_minimax_regression.py -v --tb=short
```

Result: **59 passed**.

Full local suite:

```powershell
py -3 -m pytest tests/ -v --tb=short
```

Result: **238 passed, 11 skipped, 1 warning**.

The 11 skipped tests are PostgreSQL integration tests requiring `TEST_DATABASE_URL` and the approved disposable-test database configuration. They are not counted as passed by this local run.

The warning is a Starlette deprecation warning involving the FastAPI test client/httpx integration. It did not fail the test suite.

The existing regression files cover:
- Immediate AI wins and opponent blocks horizontally, vertically, and on both diagonals; the demo win/block positions are parameterized over EASY/MEDIUM/HARD.
- Engine output contract and legal coordinates; malformed coordinates/scores and out-of-bounds or occupied moves from the search layer; controlled no-legal-move behavior on a full board.
- Board immutability for `find_best_move` on empty, midgame, near-win and depth-3 positions, and for `get_ai_move` at all three difficulties.
- Minimax horizon win/block detection, alpha-beta score parity on reference positions, incremental-evaluation equivalence, and false-positive terminal-state regressions.

Lint:

```powershell
py -3 -m flake8 app tests scripts --count --max-complexity=10 --max-line-length=127 --statistics
```

Result: **0 Flake8 issues**.

`git diff --check`: passed.

These are local Windows validation results on the stated Phase 4 SHA. They are not a substitute for a dedicated Linux/PostgreSQL acceptance run.

## 5. Linux/Docker benchmark

**Status: NOT RUN / EVIDENCE NOT YET ATTACHED.**

The Linux/Docker benchmark must use the same benchmark source SHA as the Windows run:

`2b4e3c167d7ca0a2a5b530b7a251ced6dd37d526`

Required protocol:
- 11 fixtures × 3 difficulties.
- 5 measured trials + 1 warm-up per fixture/difficulty.
- 198 raw records.
- Separate Linux/Docker CSV, JSON and Markdown outputs.
- Record Linux OS, Python runtime, CPU, Docker/image details and container resource limits.
- Record the exact command and full source SHA.

Do not combine Windows and Linux measurements into one environment report.

Owner/dependency: M4.

## 6. Proposed latency target — not an adopted SLO

**M1 clarification received:** p95 **≤ 2,000 ms** is a proposed performance target, not a formally adopted service-level objective (SLO).

M2 therefore reports the measured latency against this proposal only. It does not claim that an SLO has been accepted or achieved. All three Windows aggregate p95 measurements are below 2,000 ms for the captured, equally weighted fixture workload, but this does not establish production-tail performance. The five-trial per-fixture p95 and workload aggregate must not be presented as production traffic guarantees.

**M2-06 status: CLARIFIED.** The threshold is classified as a proposal, not an accepted SLO. Any later decision to adopt it as a formal SLO belongs to M1/team and is not a blocker to accurately documenting the current M2 measurement evidence.

## 7. Remaining M2 acceptance work

| Item | Status | Owner/dependency |
|---|---|---|
| Tactical and benchmark regression tests | PASSED on Phase 4 develop SHA | M2 |
| Windows benchmark and raw artifacts (including root-level CSV/JSON deliverables) | PASSED | M2 |
| Difficulty depth/candidate configuration and demo-midgame latency comparison | VERIFIED | M2 |
| Demo-board tactical interpretation and evaluator/search limitations | DOCUMENTED | M2 |
| Linux/Docker benchmark on matching source SHA | NOT RUN / pending evidence | M4 |
| p95 ≤ 2,000 ms classification | CLARIFIED: proposed target only; not an adopted SLO | M1 clarification relayed to M2 |
| QA evidence reconciliation | PENDING | M5 |
| Issue #28 final acceptance/sign-off | OPEN | M2/M1/M4/M5 |

Do not close Issue #28 until the Linux/Docker artifacts and M5 evidence reconciliation are available. The 2,000 ms threshold is documented as a proposal, not an accepted SLO.


## 8. M2 P1 — baseline-led optimization

The three difficulty levels have visibly different configured search budgets (depth 1/2/3 and candidate limit 6/10/14) and different measured midgame latency on the fixed demo fixture (median 2.6847/11.6002/99.5755 ms for EASY/MEDIUM/HARD). This satisfies the configuration/latency comparison using the captured Windows baseline. The same move was selected on this one midgame fixture at all three levels, so no stronger claim about different strategic behavior is made.

No optimization change set was created from this Windows baseline: there were zero measured trial failures, and the aggregate HARD p95 was 973.8549 ms against the proposed 2,000 ms performance target. M1 clarified that this threshold is not an adopted SLO; the measurement is not a formal SLO acceptance. Revisit optimization only if Linux/Docker measurements, the team's SLO decision, or further representative fixtures reveal a concrete performance or quality issue.

# CaroAI — Current Benchmark Evidence Index (2026-11-07)

**Production baseline:** `42ee035ab42cd4c0bc934699f4d5433ff4b12a83`  
**Production deployment:** `dep-dbn02vrncjis73am3dhg`, live on Render  
**Important:** Phase C measurements below were collected on a feature branch / disposable PostgreSQL runner. They do not represent production traffic and the Phase C code is not deployed.

## Current evidence

| Phase | Evidence | Result | Scope |
|---|---|---|---|
| Phase A — controlled Minimax | [Workflow #42237743095](https://github.com/emt0147t/caroAI/actions/runs/42237743095) | 1,320 measured calls, 0 failures | 11 fixtures × 4 difficulties × 30 trials; Ubuntu 24.04 / Python 3.11 |
| Phase B — API/PostgreSQL Windows review | `phaseb-20261106T140340Z-980e7124`; [review note](benchmark-phase-b/PYTHON311-WINDOWS-REVIEW.md) | Qualified historical evidence; 2,401 correctness checks reported, 0 failures | Windows 10 / Python 3.11.9 / PostgreSQL 15.19; exact original source files were not recovered |
| Phase C — Minimax counters and latency | [Workflow #42267880120](https://github.com/emt0147t/caroAI/actions/runs/42267880120) | PASS | Source SHA `8ca52e0ed4a5a2ba4546f94978dcb0c1fb06339f`; 1,320 measured calls, 0 failures |
| Phase C — API/PostgreSQL transaction boundary | [Workflow #42267879898](https://github.com/emt0147t/caroAI/actions/runs/42267879898) | PASS | Disposable PostgreSQL 15.19; 721 correctness checks, 0 failures |
| Phase C — CI / browser E2E | [CI #42267890333](https://github.com/emt0147t/caroAI/actions/runs/42267890333); [E2E #42267890323](https://github.com/emt0147t/caroAI/actions/runs/42267890323) | PASS | Candidate branch only; production release job skipped |

### Phase B Python 3.11 — qualified historical evidence

The preserved run artifacts report **2,401 database correctness checks and 0 failures**. Forensic review could not recover the exact original benchmark harness or PostgreSQL instrumentation: the recorded SHA-256 hashes did not match any available Git blob, including unreachable objects, or the available committed/current copies. The run is useful as qualified historical evidence, but its exact source snapshot cannot be attributed and the benchmark must not be described as fully reproducible.

The preserved Phase B CSV schemas do not contain a `transaction_count` column. Do not claim that `transaction_count` was measured in this Phase B run. Later instrumentation changes that add a transaction count do not establish what the unrecovered Phase B source measured.

## Phase A controlled benchmark — corrected search-only interpretation

Five of the 11 fixtures take root tactical shortcuts (immediate win or forced block) and must not be treated as representative recursive-search samples. On the six fixtures that exercise recursive search, the 180 samples per difficulty produced:

| Difficulty | Search P50 (ms) | Search P95 (ms) | Max (ms) |
|---|---:|---:|---:|
| EASY | 6.23 | 12.77 | 12.98 |
| MEDIUM | 29.25 | 61.73 | 65.28 |
| HARD | 235.82 | 523.46 | 527.77 |
| IMPOSSIBLE | 1,110.04 | 2,254.37 | 2,275.30 |

The worst IMPOSSIBLE fixture was `mid_game_spread`, with 109 root candidates and P95 approximately 2,271 ms. These are fixed-fixture hosted-runner measurements, not a production traffic percentile or an adopted SLO.

## Phase C controlled search metrics

The Phase C report records node count, average branching factor, alpha-beta pruning and candidate-cap pruning separately. On six true recursive-search fixtures:

| Difficulty | Mean nodes | Mean branching factor | Alpha-beta pruned | Candidate-cap pruned | Search P95 (ms) |
|---|---:|---:|---:|---:|---:|
| EASY | 7 | 6.00 | 0.0% | 88.6% | 12.76 |
| MEDIUM | 35 | 10.00 | 69.6% | 83.2% | 62.36 |
| HARD | 312 | 14.00 | 53.8% | 77.8% | 523.09 |
| IMPOSSIBLE | 1,576 | 20.00 | 80.5% | 71.1% | 2,277.00 |

IMPOSSIBLE by-fixture P95: `demo_midgame_search` 563 ms; `opening_two_stones` 983 ms; `opening_six_stones` 795 ms; `mid_game_spread` 2,310 ms; `edge_midgame` 1,656 ms; `dense_midgame_34_stones` 1,273 ms.

## Time-budget experiment — no production default adopted

| IMPOSSIBLE variant | Search P50 (ms) | Search P95 (ms) | Max (ms) | Timeouts |
|---|---:|---:|---:|---:|
| No budget | 867.4 | 1,730.7 | 1,742.6 | 0 |
| 1,500 ms budget | 585.4 | 1,156.1 | 1,167.0 | 0 |
| 2,000 ms budget | 1,125.1 | 2,000.5 | 2,000.6 | 30 |

The runs used separate hosted runners; latency differences are not evidence of a budget-induced speedup. The 1,500 ms budget was not reached. All 30 `mid_game_spread` samples reached the 2,000 ms budget and returned a deterministic legal fallback. Because strategic quality of that interrupted fallback has no independent oracle, neither a time budget nor a concurrency limit is enabled by default.

## Phase C API/PostgreSQL transaction-boundary results

Single request / IMPOSSIBLE: API P95 581 ms; engine P95 573 ms; summed transaction-duration P95 5.9 ms; DB connection-hold P95 5.9 ms.

Two concurrent IMPOSSIBLE requests on different games: API P95 1,170 ms; engine P95 1,146 ms; transaction-duration and connection-hold P95 approximately 45.7 ms; no PostgreSQL row-lock wait was sampled.

Two concurrent IMPOSSIBLE requests on the same game: API P95 1,151 ms; engine P95 1,136 ms; transaction-duration and connection-hold P95 approximately 35.2 ms. The request against a stale snapshot is rejected with HTTP 409 after locked state revalidation. This is expected concurrency control, not an unhandled server error.

The benchmark used one API worker and disposable PostgreSQL 15.19. It does not establish multiple-worker behavior, isolate Python GIL effects, or prove production P95. PostgreSQL lock monitoring used 10 ms sampling, and pool checkout wait was not directly instrumented.

## Phase C implementation status and links

Detailed Phase C report: [PHASE_C_BENCHMARK_REPORT.md](https://github.com/emt0147t/caroAI/blob/feat/phase-c-ai-observability-qa-20261106/reports/benchmark-phase-c/PHASE_C_BENCHMARK_REPORT.md).

Phase C source branch: `feat/phase-c-ai-observability-qa-20261106`; tested runtime source SHA: `8ca52e0ed4a5a2ba4546f94978dcb0c1fb06339f`. Phase C [PR #60](https://github.com/emt0147t/caroAI/pull/60) and follow-up PostgreSQL integration-test [PR #62](https://github.com/emt0147t/caroAI/pull/62) are merged into `develop`; PR #62 merged at `3d38d4c47ed16e788e99b4836e6157dd5ecc5dcd`. The PostgreSQL-backed acceptance integration test is complete in `develop`. Phase C is not promoted to `main` or deployed, and live production PvP/PvAI acceptance remains pending.

**Performance objective:** 2,000 ms remains a proposed engineering reference, not an adopted SLO. Do not present hosted-runner numbers as a production guarantee.

---


# Historical record — CaroAI Phase 4 M2 AI Regression and Benchmark Evidence

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

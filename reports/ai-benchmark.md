
# CaroAI Phase 4 — M2 AI Regression and Benchmark Evidence

**Overall status: PARTIAL — Windows evidence and local regression validation complete; Linux/Docker and SLO confirmation pending.**

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

### Environment

- OS: Windows 11 (`Windows-11-10.0.26200-SP0`)
- Python: 3.13.14, 64-bit
- Machine: AMD64
- CPU identifier captured by the script: `Intel64 Family 6 Model 191 Stepping 2, GenuineIntel`
- Container: not detected

The captured CPU identifier is a platform string and does not establish a verified CPU SKU.

### Raw artifacts

- [Windows CSV](benchmark-windows-phase4-2b4e3c1/ai-benchmark.csv)
- [Windows JSON](benchmark-windows-phase4-2b4e3c1/ai-benchmark.json)
- [Windows detailed report](benchmark-windows-phase4-2b4e3c1/ai-benchmark.md)

JSON validation confirmed the full source SHA, 11 fixtures, 198 records, 165 measured trials, 33 warm-ups and zero measured failures.

## 3. Tactical demo-board outcomes

The three fixed demo positions are defined in `reports/ai-demo-boards.json`.

| Demo | Difficulty coverage | Measured calls | Outcome |
|---|---|---:|---|
| `demo_ai_win_now` | EASY/MEDIUM/HARD | 15 | Expected winning move `(7, 7)` passed |
| `demo_forced_block` | EASY/MEDIUM/HARD | 15 | Expected blocking move `(0, 1)` passed |
| `demo_midgame_search` | MEDIUM/HARD in regression tests; all difficulties in benchmark | 15 | Legal outputs; no fixed expected move |

The win-now and forced-block outcomes were correct in all measured calls. The midgame fixture is a representative legal-move/search case, not an exact-move assertion.

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

## 6. Proposed latency SLO

The proposed p95 target of **≤ 2,000 ms** remains:

**PENDING_TEAM_CONFIRMATION**

All three Windows aggregate p95 measurements are below 2,000 ms, but this does not itself constitute formal SLO acceptance. The five-trial per-fixture p95 and equal-weight fixture aggregate must not be presented as production traffic guarantees.

Owner/dependency: M1 and team decision.

## 7. Remaining M2 acceptance work

| Item | Status | Owner/dependency |
|---|---|---|
| Tactical and benchmark regression tests | PASSED on Phase 4 develop SHA | M2 |
| Windows benchmark and raw artifacts | PASSED | M2 |
| Linux/Docker benchmark on matching source SHA | NOT RUN / pending evidence | M4 |
| Formal p95 SLO decision | PENDING TEAM CONFIRMATION | M1/team |
| QA evidence reconciliation | PENDING | M5 |
| Issue #28 final acceptance/sign-off | OPEN | M2/M1/M4/M5 |

Do not close Issue #28 until the Linux/Docker artifacts, SLO decision and M5 evidence reconciliation are available.

# CaroAI Phase C — AI and API/PostgreSQL Performance Evidence

**Benchmark source SHA:** `8ca52e0ed4a5a2ba4546f94978dcb0c1fb06339f`  
**Production baseline SHA:** `42ee035ab42cd4c0bc934699f4d5433ff4b12a83`  
**Date:** 2026-11-07 (Asia/Bangkok)  
**Production deployment:** unchanged; no production benchmark or deployment was performed.

## Executive result

| Area | Evidence | Result |
|---|---|---|
| Minimax counters and fixture latency | [AI benchmark workflow #42267880120](https://github.com/emt0147t/caroAI/actions/runs/42267880120), 11 × 4 × 30 measured + 3 warmups | PASS; 1,320 measured calls, 0 failures |
| API/PostgreSQL concurrency and transaction boundary | [API/DB workflow #42267879898](https://github.com/emt0147t/caroAI/actions/runs/42267879898), PostgreSQL 15.19 | PASS; 721 correctness checks, 0 failures |
| Python/Flake8, PostgreSQL acceptance, Compose restart persistence, secret scan, Docker build | [CaroAI CI #42267890333](https://github.com/emt0147t/caroAI/actions/runs/42267890333) | PASS; production release job skipped |
| Browser E2E / visual regression | [Browser E2E #42267890323](https://github.com/emt0147t/caroAI/actions/runs/42267890323) | PASS |
| Production PvP/PvAI live acceptance | QA runner is installed in the approved release path, but the new migration/API is not deployed | NOT RUN — explicit release approval required |
| Render CPU/memory/platform HTTP telemetry | Requires confirmed Render workspace | PENDING |

## 1. Controlled Minimax benchmark

### Environment and protocol

- Ubuntu 24.04 / Python 3.11.18 / Linux x86_64; precise CPU SKU was not available, so cross-run CPU equivalence is not claimed.
- Full source SHA: `8ca52e0ed4a5a2ba4546f94978dcb0c1fb06339f`.
- 11 fixtures × 4 difficulty levels × 30 measured trials + 3 warmups = 1,452 rows; 1,320 measured.
- Percentile method: nearest rank. Each difficulty has 330 measured calls; search-only results below exclude five root tactical shortcut fixtures.
- All 1,320 measured calls had valid output shape, legal coordinates, unchanged input board, and zero benchmark failures. Forced-win and forced-block positions passed 30/30 for each difficulty.

### Search-only latency and work counters

Six true recursive-search fixtures: `demo_midgame_search`, `opening_two_stones`, `opening_six_stones`, `mid_game_spread`, `edge_midgame`, `dense_midgame_34_stones`.

| Difficulty | n | Search P50 (ms) | Search P95 (ms) | Max (ms) | Mean nodes | Mean branching | Alpha-beta pruned | Candidate-cap pruned |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| EASY | 180 | 5.65 | 12.76 | 12.93 | 7 | 6.00 | 0.0% | 88.6% |
| MEDIUM | 180 | 27.97 | 62.36 | 64.25 | 35 | 10.00 | 69.6% | 83.2% |
| HARD | 180 | 232.36 | 523.09 | 528.32 | 312 | 14.00 | 53.8% | 77.8% |
| IMPOSSIBLE | 180 | 1,118.58 | 2,277.00 | 2,320.25 | 1,576 | 20.00 | 80.5% | 71.1% |

### IMPOSSIBLE by fixture

| Fixture | P50 (ms) | P95 (ms) | Max (ms) | Mean nodes | Alpha-beta pruned | Candidate-cap pruned |
|---|---:|---:|---:|---:|---:|---:|
| `demo_midgame_search` | 543.09 | 562.76 | 587.65 | 780 | 90.2% | 63.5% |
| `opening_two_stones` | 971.92 | 982.89 | 984.27 | 1,645 | 85.8% | 55.1% |
| `opening_six_stones` | 789.91 | 795.23 | 800.02 | 1,350 | 85.9% | 62.2% |
| `mid_game_spread` | 2,269.23 | 2,310.15 | 2,320.25 | 2,400 | 83.0% | 82.0% |
| `edge_midgame` | 1,640.19 | 1,655.69 | 1,668.82 | 2,185 | 82.8% | 76.6% |
| `dense_midgame_34_stones` | 1,261.44 | 1,272.57 | 1,277.55 | 1,096 | 55.1% | 87.2% |

The `dense_midgame_42_stones`, `competing_open_threes`, and `complex_mid_game` positions trigger root tactical shortcuts; their very low latency is not recursive-search evidence. Do not mix them into search-only latency.

### Budget experiment and operating decision

Three separate Ubuntu runner jobs used the same earlier AI-source SHA `abe644a67f4360480110d68554a11036edf81a09`; exact CPU SKU was not available. These are useful bounded-search experiments, but timing differences between separate hosted runners must not be interpreted as a speedup from the budget.

| IMPOSSIBLE variant | Search P50 (ms) | Search P95 (ms) | Max (ms) | Timeouts |
|---|---:|---:|---:|---:|
| No budget | 867.4 | 1,730.7 | 1,742.6 | 0 |
| 1,500 ms budget | 585.4 | 1,156.1 | 1,167.0 | 0 |
| 2,000 ms budget | 1,125.1 | 2,000.5 | 2,000.6 | 30 |

The 1,500 ms setting was not reached in any of the six search fixtures. At 2,000 ms, all 30 `mid_game_spread` trials hit the deadline and returned a deterministic legal fallback. The configured budget starts after mandatory root immediate-win / forced-block scans, and outer engine validation is included in reported elapsed time; therefore measured time can slightly exceed the configured limit.

**Production decision:** keep `CAROAI_IMPOSSIBLE_TIME_BUDGET_MS` unset for now. A timeout fallback is legal but its strategic quality on the interrupted fixture has no independent oracle result. Keep `CAROAI_IMPOSSIBLE_MAX_CONCURRENCY=0` (unlimited) and `CAROAI_IMPOSSIBLE_QUEUE_WAIT_MS=0` (no guard wait) unless a host-specific capacity decision is made. The process-local guard is not a global/distributed concurrency limit.

## 2. API/PostgreSQL transaction-boundary benchmark

### Environment and protocol

- Workflow [#42267879898](https://github.com/emt0147t/caroAI/actions/runs/42267879898).
- Source SHA: `8ca52e0ed4a5a2ba4546f94978dcb0c1fb06339f`.
- Ubuntu 24.04 / Python 3.11.18 / PostgreSQL 15.19 / one API worker / 10 ms `pg_stat_activity` sampling.
- 30 measured trials + 3 warmups per workload group, four difficulties and concurrency 1/2.
- 22 groups: 20 primary groups plus two read-under-AI-load groups. Read-under-load remains a small 1/2 sample, not a stable percentile.
- 843 client request rows, 5,686 server metric rows, 17,272 PostgreSQL observation rows.
- 721 database correctness checks, zero failures; no PostgreSQL monitor error; clean benchmark working tree; peak active database connections: 2.
- Same-game c=2 groups had 30 successful moves and 30 expected HTTP 409 stale-snapshot conflicts per difficulty; zero unexpected errors. The raw server CSV also includes warmups and one pre-search HTTP 400 `not the AI turn` race, which the harness classifies as an expected conflict. No invalid successful AI responses were observed.

### Single request per difficulty

| Difficulty | API P50 (ms) | API P95 (ms) | Engine P95 (ms) | Transaction sum P95 (ms) | Connection hold P95 (ms) |
|---|---:|---:|---:|---:|---:|
| EASY | 9.1 | 23.6 | 3.7 | 3.6 | 3.6 |
| MEDIUM | 19.4 | 31.3 | 14.7 | 13.5 | 13.5 |
| HARD | 132.4 | 138.1 | 129.4 | 5.1 | 5.2 |
| IMPOSSIBLE | 555.9 | 581.4 | 573.3 | 5.9 | 5.9 |

### Different games, concurrency 2

| Difficulty | API P50 (ms) | API P95 (ms) | Engine P95 (ms) | Transaction sum P95 (ms) | Connection hold P95 (ms) | Throughput (req/s) |
|---|---:|---:|---:|---:|---:|---:|
| EASY | 15.0 | 28.2 | 3.3 | 19.5 | 19.5 | 109.7 |
| MEDIUM | 35.8 | 56.6 | 23.9 | 25.4 | 25.4 | 51.9 |
| HARD | 263.3 | 275.3 | 258.3 | 19.8 | 19.8 | 7.6 |
| IMPOSSIBLE | 1,135.6 | 1,170.1 | 1,145.7 | 45.7 | 45.8 | 1.75 |

No PostgreSQL lock wait was sampled for different-game concurrency. The API tail remains dominated by AI compute/CPU contention in the one-worker benchmark, not row-lock wait. This benchmark does not isolate Python GIL effects from scheduler/CPU constraints.

### Same game, concurrency 2

| Difficulty | 2xx successes | HTTP 409 stale conflicts | API P95 (ms) | Engine P95 (ms) | Transaction sum P95 (ms) | Connection hold P95 (ms) |
|---|---:|---:|---:|---:|---:|---:|
| EASY | 30 | 30 | 24.9 | 3.3 | 14.8 | 14.8 |
| MEDIUM | 30 | 30 | 41.5 | 24.5 | 15.4 | 15.5 |
| HARD | 30 | 30 | 280.3 | 258.8 | 25.0 | 25.0 |
| IMPOSSIBLE | 30 | 30 | 1,150.5 | 1,136.1 | 35.2 | 35.2 |

Each pair deliberately starts from the same saved game snapshot. One request commits; the second recalculates against the old snapshot, then is rejected with HTTP 409 after reloading under `FOR UPDATE`. The API never overwrites the committed move. This is expected optimistic-concurrency behavior, not a server failure.

### Transaction-boundary evidence and limitations

- All successful and stale AI requests showed two root transaction spans in server instrumentation: one short snapshot read and one short lock/revalidate/write transaction. The engine ran outside those spans.
- For a single IMPOSSIBLE request, engine P95 was 573 ms while the sum of root transaction durations and connection-hold P95 were both about 5.9 ms.
- For different-game IMPOSSIBLE concurrency 2, engine P95 was 1,146 ms, while transaction and connection-hold P95 were about 45.7 ms.
- `row_lock_query_ms` includes SQL execution and any row-lock wait; it is not a pure lock-wait timer. PostgreSQL `pg_stat_activity` is polled at 10 ms, so observed lock-wait percentiles are sampled/quantized lower-bound indicators.
- SQLAlchemy checked-out connection gauge and `db_connection_hold_ms` are per process. Pool checkout wait is not directly instrumented.
- The single API worker means this run does not establish behavior for multiple Uvicorn workers or multiple Render instances.

## 3. Phase C design changes

- Minimax now emits nodes, leaves, root candidates, generated/expanded candidates, candidate-cap rejections, alpha-beta cutoffs/pruned edges, branching and timeout/shortcut results.
- Candidate-cap pruning and alpha-beta pruning are separate ratios with documented denominators.
- Optional IMPOSSIBLE time budget and process-local admission guard are disabled by default.
- AI move computation is outside a DB transaction; commit requires a locked re-read and full game-state equality. Stale state returns 409.
- QA games receive a nullable exact-run ID, created only by the dedicated QA route; cleanup deletes analysis, moves and games for that exact run.
- Prometheus `/metrics` is disabled by default and requires `CAROAI_METRICS_TOKEN` + bearer authorization when enabled. Alert rules are templates only.

## 4. Validation and remaining acceptance

- CI on source SHA `8ca52e0ed4a5a2ba4546f94978dcb0c1fb06339f`: Python tests/Flake8, frontend regression, dedicated PostgreSQL acceptance, Compose persistence after app restart, secret scan and Docker build all passed; production release job skipped.
- Browser E2E / visual regression on the same SHA passed.
- AI engine controlled benchmark on the same SHA passed with 1,320 measured calls and zero failures.
- Full PostgreSQL API/DB contention matrix passed with 721 correctness checks and zero failures.
- The new production acceptance runner is not yet run against the live website because the QA routes and migration are not deployed. It is wired behind the authorized production release job after exact-SHA deploy and read-only smoke checks.
- Render CPU/memory, platform HTTP latency and database provider metrics have not been queried; user confirmation of the target Render workspace is required. No Prometheus server, Alertmanager or notification destination is configured by the PR.

**Threshold note:** the 2,000 ms reference remains a proposed performance target, not an accepted SLO. Do not describe this evidence as a production traffic SLO.

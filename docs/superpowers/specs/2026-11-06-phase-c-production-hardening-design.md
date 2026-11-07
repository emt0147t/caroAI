# Phase C & Production Hardening — Design

> **Historical design:** The original run-ID-only QA authentication proposal below is superseded by the follow-up implementation described in [Production QA Acceptance Security](../../operations/qa-acceptance-security.md). A run ID scopes cleanup but is not caller authentication.

**Date:** 2026-11-06  
**Baseline:** `42ee035ab42cd4c0bc934699f4d5433ff4b12a83`  
**Production service:** `srv-dbkd2dflk1mc73fd2ukg`

## Intent

Improve CaroAI's engineering readiness after the November 6 production release. The work covers measurable AI search cost, shorter database lock/connection occupancy, a controlled and cleanable live QA flow, and low-cardinality application telemetry that can be correlated with Render's resource metrics.

## Goals

1. Measure Minimax node count, generated/expanded candidates, candidate-cap pruning, alpha-beta pruning, effective branching factor, and elapsed time by fixture and difficulty.
2. Provide an opt-in time budget and an opt-in per-process admission guard for IMPOSSIBLE searches. Preserve current behavior when neither setting is configured.
3. Compute an AI move without holding a PostgreSQL transaction or row lock; acquire the lock only for state revalidation and persistence.
4. Add run-scoped QA creation and cleanup so production PvP/PvAI smoke records can be deleted without touching ordinary user games.
5. Record bounded-cardinality HTTP, AI, SQL, connection-pool, and transaction metrics, and define alert thresholds.

## Non-goals

- No change to game rules, heuristic weights, default depth/candidate limits, or AI difficulty names.
- No guarantee that IMPOSSIBLE is unbeatable; it remains bounded heuristic search.
- No production load test or uncontrolled request flood.
- No new hosted queue/Redis service or distributed scheduler in this phase.
- No production environment-variable changes or Render deploy as part of the implementation PR.
- No claim that Render platform metrics are available until the intended workspace is explicitly selected.

## Approaches considered

### AI concurrency: distributed queue vs process-local admission guard

A distributed queue/worker architecture would provide cross-instance scheduling, durable work and better back-pressure, but it adds Redis/Valkey, a worker service, queue semantics, and deployment cost. A process-local semaphore is much smaller and testable for the current single web-service instance. **Chosen:** configurable process-local admission guard, default disabled, with explicit documentation that its limit is per process and must be replaced by distributed admission if the app is scaled to multiple workers/instances.

### AI transaction boundary: keep the lock vs optimistic compute/revalidate

Keeping the current `SELECT ... FOR UPDATE` across Minimax guarantees the board cannot change, but holds a DB connection and row lock for the entire search. Computing before locking reduces resource occupancy but introduces stale-search races. **Chosen:** read an immutable logical snapshot in a short read transaction, compute outside a transaction, then lock/reload and compare board, move count, turn, mode and terminal state before persisting. If the position changed, return HTTP 409; never persist a move derived from stale state. No automatic retry in this iteration.

### Production QA cleanup: delete public game IDs vs run-scoped capability

A general game-delete endpoint is unsafe because it could remove user data. **Chosen:** add a nullable `qa_run_id` column and dedicated QA creation/cleanup routes. A cryptographically random 128-bit run ID is supplied in a header; cleanup deletes only games tagged with that exact ID, including dependent moves/analysis rows, in one transaction. Normal game creation cannot set this field. The acceptance runner always attempts cleanup in a `finally` path and verifies the games are no longer readable.

### Observability: provider-specific agent vs Prometheus metrics

Adding an external hosted observability product would require credentials, billing and account configuration that are not part of the request. **Chosen:** export standard Prometheus metrics from the app with the existing Python stack plus `prometheus-client`; use Render's service metrics for CPU, memory and HTTP latency. This provides an interoperable source without committing to an external vendor. Alert rules are documented; no paging integration is configured in this phase.

## Architecture and behavior

### Search instrumentation and budget

- Add an optional mutable search-statistics object passed through recursive Minimax calls.
- Count visited nodes, leaves, generated candidates, candidate-cap rejections, actually expanded child edges, alpha-beta cutoffs and remaining edges skipped by each cutoff.
- Define alpha-beta pruning rate only over candidates remaining after the configured candidate cap; report candidate-cap pruning separately.
- A configured time budget applies to recursive search after mandatory root immediate-win/immediate-block checks. If it expires, return a deterministic legal fallback and mark the result as timed out. The budget does not imply a proven best move.
- `CAROAI_IMPOSSIBLE_TIME_BUDGET_MS` is unset by default; no production behavior changes until explicitly configured.

### Admission control

- `CAROAI_IMPOSSIBLE_MAX_CONCURRENCY=0` means unlimited (the default).
- A positive value limits concurrent IMPOSSIBLE searches in one process.
- `CAROAI_IMPOSSIBLE_QUEUE_WAIT_MS=0` fails fast when capacity is full; positive values allow a bounded wait.
- Rejected requests return HTTP 429 and a `Retry-After` hint. EASY/MEDIUM/HARD are not limited by the IMPOSSIBLE guard.

### Transaction revalidation

- Snapshot read and AI computation happen without a row lock.
- The write transaction reloads under `FOR UPDATE`.
- Compare the full domain state relevant to choosing a move.
- A concurrent human/AI move or terminal transition causes HTTP 409 and no write.
- The transaction contains only lock/read/revalidation/insert/update/commit work.

### QA data lifecycle

- `POST /api/qa/games` requires `X-CaroAI-QA-Run-ID` in 32-character lowercase hex.
- The route uses the normal server-authoritative GameService but tags the game with that run ID.
- `DELETE /api/qa/runs` requires the same header and deletes only tagged games.
- The production acceptance runner creates a PvP win and one PvAI response, verifies game details/history after separate GET requests, and removes all records in a `finally` block.
- The runner reports the run ID only if cleanup fails, so an operator can perform the narrow cleanup.

### Metrics

Expose `/metrics` with bounded labels:
- HTTP request count and duration by method, normalized route and status.
- AI search latency, nodes, branching and pruning by difficulty and timeout/shortcut outcome.
- SQL statement duration by operation and row-lock flag.
- DB connection checked-out gauge and connection-hold duration.
- SQLAlchemy transaction duration.
Never use raw game IDs, request IDs, SQL text, query parameters, or run IDs as metric labels.

Render CPU/memory/request latency remain platform-level metrics. Alert thresholds in documentation are initial operational recommendations, not formally adopted SLOs.

## Constraints and rollout

- Database migration is additive: `002_games_qa_run_id.sql`.
- Existing rows retain `qa_run_id = NULL`.
- QA deletion must delete dependent analysis and move rows before game rows.
- Existing release flow remains the only production deploy path.
- No production QA run occurs until the updated application is deployed by the approved release workflow.
- The Render workspace must be explicitly confirmed before querying its platform metrics.

## Acceptance criteria

- Unit tests cover search counters, alpha-beta pruning accounting, candidate-cap accounting, deadline behavior, legal fallback, and input validation.
- Service tests prove AI search runs outside the write transaction and stale state is rejected without persisting a move.
- PostgreSQL acceptance tests apply migration 002 and prove QA cleanup removes only matching run records and their children.
- Browser E2E remains green.
- Production QA script verifies PvP terminal win, PvAI turn, fresh GET read-back, history inclusion and cleanup.
- `/metrics` exports the documented metric families without unbounded labels.
- CI tests, PostgreSQL acceptance and Docker build pass before merge; live production QA is run only after a later approved deploy.

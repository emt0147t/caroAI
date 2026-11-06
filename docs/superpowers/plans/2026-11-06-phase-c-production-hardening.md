# Phase C & Production Hardening Implementation Plan

> **For agentic workers:** use the executing-plans workflow task by task. Steps use checkbox syntax and should be checked only with fresh evidence.

**Goal:** Instrument and bound AI search cost, shorten AI transaction lock duration safely, provide cleanable production QA data, and export application/runtime metrics.

**Architecture:** Minimax emits explicit search counters and optional budget interruption; GameService computes from a read snapshot and revalidates under a short write lock. QA records are tagged by a new nullable run ID column and deleted through a narrowly scoped cleanup route. Prometheus metrics use bounded labels, with Render supplying host CPU/memory/HTTP metrics.

**Tech Stack:** Python 3.11, FastAPI, SQLAlchemy, PostgreSQL, pytest, Prometheus client, GitHub Actions, Render.

**Spec:** `docs/superpowers/specs/2026-11-06-phase-c-production-hardening-design.md`

## Global Constraints

- Preserve the 15×15 board, turn rules, result semantics, difficulty labels and existing API response schema.
- Preserve current AI behavior when time-budget and IMPOSSIBLE concurrency variables are unset.
- Never persist an AI move computed from a state that changed while search was running.
- QA cleanup must only delete games carrying the exact matching run ID.
- Never place IDs/tokens/SQL/user content in Prometheus labels.
- Do not run load tests against the public production site.
- Do not claim production PvP/PvAI acceptance until the separate QA runner finishes and cleanup is verified.
- Use the current protected-main release workflow; no direct production deploy from feature branches.

## Review Focus

- A forced deadline on the first recursive node must still return an in-bounds empty cell.
- Immediate root wins and blocks must remain honored even when a search time budget is configured.
- Two concurrent AI requests from the same snapshot must not commit the same turn twice.
- A concurrent human move during AI search must produce HTTP 409, not overwrite the human move.
- Cleanup of a run with no games, multiple games, and dependent analyses/moves must be safe and idempotent.
- Invalid or malformed QA run IDs must be rejected; ordinary create-game requests must never set QA metadata.
- HTTP paths with game IDs and QA run IDs must normalize to fixed metric labels.

---

### Task 1: Minimax instrumentation and bounded time budget

**Files:**
- Create: `app/ai/search_stats.py`
- Modify: `app/ai/minimax.py`
- Modify: `app/ai/engine.py`
- Create: `tests/unit/test_ai_search_stats.py`
- Modify: `tests/unit/test_ai_engine.py`

- [ ] Add tests for node/leaf/candidate/cutoff counters and pruning-rate definitions.
- [ ] Add a test proving candidate-cap removals are counted separately from alpha-beta pruning.
- [ ] Add a test proving a tiny time budget returns a legal fallback and marks the result timed out.
- [ ] Add tests proving mandatory root win/block shortcuts remain honored with a budget.
- [ ] Add optional stats/deadline plumbing through recursive Minimax.
- [ ] Add optional `collect_stats` and `time_budget_ms` parameters to the engine while preserving the existing result keys.
- [ ] Verify tests and engine immutability/regression suites.

### Task 2: IMPOSSIBLE admission guard and transaction boundary

**Files:**
- Create: `app/ai/admission.py`
- Modify: `app/services/game_service.py`
- Modify: `app/api/routes_games.py`
- Modify: `tests/test_game_service.py`
- Modify: `tests/test_games_api.py`
- Modify: `tests/test_repository_persistence.py`

- [ ] Add deterministic unit tests for guard capacity, wait timeout, and non-IMPOSSIBLE pass-through.
- [ ] Add a stale-snapshot service test in which a human move commits while the fake AI engine is running.
- [ ] Add a test that verifies a stale AI result is not persisted.
- [ ] Add an API test for HTTP 409 stale-state conflict and HTTP 429 admission rejection.
- [ ] Read game state in a short transaction, run Minimax outside a transaction, then lock/re-read/revalidate and persist.
- [ ] Ensure the revalidation covers board, move count, current player, mode, status and winner.
- [ ] Verify SQLite persistence and the dedicated PostgreSQL acceptance suite.

### Task 3: Production QA tagging and cleanup

**Files:**
- Create: `database/migrations/002_games_qa_run_id.sql`
- Modify: `app/db/models.py`
- Modify: `app/db/repository.py`
- Modify: `app/services/game_service.py`
- Create: `app/api/routes_qa.py`
- Modify: `app/main.py`
- Create: `scripts/production_qa_acceptance.py`
- Modify: `tests/test_repository_persistence.py`
- Create: `tests/test_qa_api.py`
- Modify: `.github/workflows/ci-cd.yml`

- [ ] Add SQLite/PostgreSQL tests for the nullable QA tag and exact-run cleanup.
- [ ] Prove cleanup deletes child rows before parent games and leaves non-QA rows unchanged.
- [ ] Apply the additive versioned migration before serving the new code.
- [ ] Add dedicated QA creation and cleanup routes; do not add a general public game-delete route.
- [ ] Write an HTTP-standard-library acceptance runner that checks PvP win, PvAI response, new-session read-back, history inclusion and cleanup in a `finally` block.
- [ ] Integrate the runner after production read-only smoke checks in the release job.
- [ ] Unit-test the runner helpers using a local test server; live production execution happens only after the updated release is approved and deployed.

### Task 4: Prometheus observability and operational thresholds

**Files:**
- Modify: `requirements.txt`
- Create: `app/observability.py`
- Modify: `app/main.py`
- Modify: `app/db/database.py`
- Modify: `app/services/game_service.py`
- Create: `tests/test_observability.py`
- Create: `docs/operations/observability-and-alerts.md`
- Create: `ops/monitoring/caroai-alerts.yml`

- [ ] Add tests for HTTP route normalization and metrics output.
- [ ] Add tests proving raw game IDs/query text are never metric labels.
- [ ] Instrument SQLAlchemy connection checkout/checkin, statement duration and root transaction duration.
- [ ] Instrument AI search duration/node/branch/pruning metrics.
- [ ] Expose `/metrics` with bounded labels and document platform-vs-application metrics.
- [ ] Define warning/critical alert expressions with explicit windows; mark them initial thresholds rather than accepted SLOs.
- [ ] Verify existing health/readiness endpoints and full test suites.

### Task 5: Documentation and review

**Files:**
- Modify: `README.md`
- Modify: `docs/final-project/FINAL_ACCEPTANCE_REPORT.md`
- Modify: `docs/final-project/PRODUCTION_PREFLIGHT.md`
- Modify: `reports/ai-benchmark.md`
- Create/update: Phase C benchmark report after a real run.

- [ ] Document new environment variables, semantics and default-disabled behavior.
- [ ] Document QA run/cleanup behavior and operational recovery if cleanup fails.
- [ ] Document metric names, label cardinality, thresholds and Render platform metric dependencies.
- [ ] Update benchmark tables only with raw Phase C evidence; do not invent result numbers.
- [ ] Open PR to `develop`; require CI, PostgreSQL acceptance and Browser E2E before any promotion to `main`.

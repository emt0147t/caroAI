# CaroAI — Phase A Complete Repository Audit
**Role**: Principal Software Engineer & Tech Lead & DevOps Engineer & QA Lead  
**Date**: November 2, 2026  
**Repository**: `emt0147t/caroAI`  
**Current Baseline Develop SHA**: `432d8ccbe8ea03406cc1ec9f4aa9f7c44f805258`  
**Current Main SHA**: `d444119d5eb757e364f904bb9eacddd27e14e507`  

---

## 1. Executive Summary & Audit Context

This audit provides a comprehensive, rigorous assessment of the CaroAI repository in preparation for final project completion, release consolidation, Docker publication, persistent PostgreSQL deployment on Render, and academic demonstration.

The CaroAI system is a 15×15 Gomoku (Cờ Caro) application featuring a FastAPI backend, Minimax AI engine with alpha-beta pruning and heuristic evaluation, a responsive browser frontend, PostgreSQL database persistence, Docker containerization, and GitHub Actions CI/CD.

All findings below are based on direct inspection of the live Git repository, remote branches, pull requests, CI workflows, Docker configuration, database schema/migrations, and local testing.

---

## 2. Git & Branching State

### 2.1 Branch Ancestry & Commit Counts
- **`origin/develop`**:
  - Head SHA: `432d8ccbe8ea03406cc1ec9f4aa9f7c44f805258`
  - Total Commit Count: **372 commits** (substantially satisfies the university requirement of >= 30 commits).
  - Status: Healthy, protected development baseline.
- **`origin/main`**:
  - Head SHA: `d444119d5eb757e364f904bb9eacddd27e14e507`
  - Total Commit Count: **7 commits**.
  - Status: Significantly behind `develop` (367 commits behind). Contains an early repository structure before the full FastAPI backend, AI engine, and PostgreSQL persistence were merged.
  - Risk: Deploying from current `main` would fail completely. `main` must be systematically promoted from `develop` once all outstanding PRs are integrated and validated.

### 2.2 Active Pull Requests Audit
| PR # | Head Branch | Base Branch | Head SHA | State | Scope & Health Assessment |
|---|---|---|---|---|---|
| **#46** | `feature/m1-backend-acceptance-e45b077` | `develop` | `664bc9d` | Open | Strengthens PostgreSQL rollback test in `tests/postgres_suite.py` and records acceptance in `docs/m1-backend-acceptance-e45b077.md`. Branched from `e45b077` (13 commits behind `develop` `432d8cc`). Mergeable without git conflicts, but needs integration update against latest `develop`. |
| **#48** | `feature/deploy-serve-frontend` | `develop` | `60320b4` | Open | Serves static frontend directly from FastAPI app container at `/` and `/trong_tran/index.html`. Passes all CI and browser E2E tests (`Run #41438183219`, `Run #41438183222`). Crucial for single-container Render deployment. |
| **#47** | `feature/devops` | `develop` | `1fa0349` | Merged | Established robust CI/CD release workflow in `.github/workflows/ci-cd.yml`, including disposable Compose functional smoke test, full-history secret scanning, and production release gates. |
| **Unmerged** | `feature/frontend-ui-ux-revamp` | `develop` | `a24ddc7` | Local/Remote Pushed | Complete modern CaroAI home and dashboard redesign (UI-01), system health status check, arena stats, and 4 new E2E tests (`tests/e2e/dashboard.spec.cjs`). Passed CI (`Run #41433803051`). |

---

## 3. Architecture & Mismatch Analysis

### 3.1 Local Development vs. Production Runtime Discrepancy
- **Local Docker Compose (`docker-compose.yml`)**:
  - Employs a three-container topology: `db` (Postgres 15), `app` (FastAPI backend on port 8000), and `frontend` (Nginx on port 8080 proxying `/api/` and `/health` to `app:8000`).
  - Works reliably for multi-container local testing and E2E runs.
- **Production Runtime (Render Web Service)**:
  - Render Web Service runs a single Docker container derived from `Dockerfile`.
  - In `develop` baseline (`432d8cc`), `app/main.py` only serves JSON API (`/`, `/api/*`, `/health`, `/ready`). There is no Nginx container in Render.
  - **Identified Defect**: Without PR #48, a Render deployment from `develop` will serve a JSON welcome message at `/`, leaving the frontend completely inaccessible.
  - **Resolution**: PR #48 (`feature/deploy-serve-frontend`) correctly mounts the frontend static directory inside FastAPI after API routes, ensuring a single unified container serves both the API and the UI on the same origin.

### 3.2 Dockerfile Production Audit
- **Current `Dockerfile` Structure**:
  - Multi-stage build: `builder` compiles dependency wheels with `build-essential`; `runner` installs wheels, creates non-root user `appuser` (UID 10001), copies repository with ownership, and defines healthcheck.
  - Healthcheck: `HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 CMD curl -f http://localhost:8000/ready || exit 1`
  - Entrypoint / Command: `CMD ["sh", "-c", "python -m scripts.migrate_database && exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]`
- **Identified Defects & Risks**:
  1. **Hardcoded Port 8000**: Render assigns dynamic listening ports via the `$PORT` environment variable (e.g. `10000`). Hardcoding `--port 8000` causes routing or healthcheck failures when Render proxies traffic to `$PORT`.
     - *Fix*: Use `exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`.
  2. **Healthcheck Port Binding**: The in-container healthcheck hardcodes `localhost:8000/ready`. When `PORT` is overridden, healthcheck fails.
     - *Fix*: `curl -f http://localhost:${PORT:-8000}/ready || exit 1`.
  3. **Signal Handling**: Using `exec python -m uvicorn ...` properly passes SIGTERM/SIGINT to uvicorn for graceful shutdown.

### 3.3 Database & Migrations Configuration
- **PostgreSQL Connectivity**:
  - `app/db/database.py` normalizes `postgres://` to `postgresql+psycopg2://` (standardizing Render's default connection strings).
  - Uses `pool_pre_ping=True` to detect dropped connections.
  - Unbound session factory avoids runtime connection requirements during module import.
- **Migration Mechanism**:
  - `scripts/migrate_database.py` enforces explicit, idempotent, versioned SQL migrations (`000_initial_schema.sql`, `001_games_public_id.sql`).
  - Tracks execution in table `schema_migrations`.
  - Explicitly avoids unmanaged `create_all()` in production.
- **Safety Guards**:
  - `app/db/testing.py` and `tests/test_database_guard.py` fail-closed: tests require `TEST_DATABASE_URL`, confirmation `disposable-test-database`, and host allowlisting to prevent accidental database wipes or testing on production/development databases.

---

## 4. Frontend & API Contract Audit

### 4.1 API Endpoints
All endpoints are strictly defined in `app/api/` and verified:
- `POST /api/games`: Accepts `{"mode": "HUMAN_VS_HUMAN"}` or `{"mode": "HUMAN_VS_AI"}`. Returns `201 Created` with game ID, 15×15 empty board, and initial state.
- `GET /api/games/{game_id}`: Returns authoritative board, current player, move count, status (`IN_PROGRESS`, `X_WON`, `O_WON`, `DRAW`).
- `POST /api/games/{game_id}/moves`: Validates human move coordinates (`0 <= row, col <= 14`), updates board, verifies win/draw, returns updated game state.
- `POST /api/games/{game_id}/ai-move`: Invokes Minimax engine for O player with difficulty (`easy`, `medium`, `hard`).
- `GET /api/history`: Returns paginated persisted games from PostgreSQL with mode, move count, timestamps, status.
- `GET /health`: Liveness probe (returns `{"status": "ok"}`).
- `GET /ready`: Readiness probe (verifies database `SELECT 1`).

### 4.2 Frontend Integration
- Frontend codebase in `frontend/Caro_AI/` uses relative/same-origin routing by default (`window.CAROAI_API_BASE_URL || ""`), allowing seamless operation when served by Nginx or directly by FastAPI.
- In `feature/frontend-ui-ux-revamp`, `welcome.html` acts as a complete gaming hub:
  - Preserves exact element IDs and attributes for test compatibility (`[data-mode]`, `#difficultyGroup`, `#startBtn`, `#message`).
  - Adds live `/health` status check and `/api/history` recent matches widget.
  - DOM order strictly ensures keyboard Tab navigation focuses mode selection first, maintaining 100% pass on all existing UX specifications.

---

## 5. Security & Secrets Audit

1. **Secret Scanning**:
   - Gitleaks Action runs on every PR commit range.
   - Gitleaks Docker container runs a full-history scan across all branches and commits (`Run #41438183219` passed with 0 leaks).
2. **Repository File Inspection**:
   - `.env` is properly ignored in `.gitignore` and `.dockerignore`.
   - `.env.example` contains only placeholder development credentials (`replace-with-a-local-password`).
   - No production tokens, API keys, or Render deploy hooks are present in the repository files or commit logs.
3. **CI/CD Environment Security**:
   - Production secrets (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `RENDER_DEPLOY_HOOK`, `RENDER_API_KEY`, `RENDER_SERVICE_ID`) are bound to the GitHub `production` Environment, requiring explicit environment approval before execution.

---

## 6. University Requirement Reconciliation Matrix

| Requirement | Target | Current Status | Remaining Work |
|---|---|---|---|
| **Git Commits** | At least 30 meaningful commits | **PASS** (372 commits on develop) | None for count. Maintain meaningful commit messages. |
| **Git Merge Conflict** | At least 1 genuine conflict resolved & documented | **PENDING** | Create controlled conflict demonstration on non-core documentation branch, resolve, verify, and document in `docs/final-project/MERGE_CONFLICT_EVIDENCE.md`. |
| **Feature Branches & PRs** | Feature branches and PR workflow | **PASS** (Feature branch workflow active; PRs #46, #47, #48, revamp) | Consolidate PRs into develop via review and approval. |
| **Docker Build** | Working multi-stage Dockerfile | **PASS** locally and in CI build job | Patch dynamic port `${PORT:-8000}` in Dockerfile. |
| **Docker Hub Image** | Published to Docker Hub registry | **PENDING** | Execute approved CI release job targeting Docker Hub repository upon promotion to `main`. |
| **CI/CD Pipeline** | Automated Test → Build → Publish → Deploy | **CONFIGURED & TESTED** | CI passes on all branches; release job gated on `main`. |
| **PostgreSQL Database** | Persistent PostgreSQL on production | **PENDING LIVE VERIFICATION** | Validate persistent connection and data retention on Render PostgreSQL. |
| **Public HTTPS Address** | Publicly accessible app on Render | **CONFIGURED IN CI** | Deploy approved SHA to Render and record live evidence. |
| **Deliverables & README** | Comprehensive README & acceptance report | **PENDING** | Update `README.md` and generate `FINAL_ACCEPTANCE_REPORT.md`. |

---

## 7. Recommended Execution Order

1. **Phase B (Consolidate Source Code & PRs)**:
   - Step 1: Update PR #46 (`feature/m1-backend-acceptance-e45b077`) against latest `develop` baseline (`432d8cc`) without force-pushing. Verify all PostgreSQL rollback tests pass.
   - Step 2: Merge PR #46 and PR #48 (`feature/deploy-serve-frontend`) into `develop`.
   - Step 3: Merge `feature/frontend-ui-ux-revamp` into `develop`, ensuring the redesigned dashboard is served by FastAPI.
   - Step 4: Validate consolidated `develop` with full test suites (syntax, regression, pytest, compose smoke, Playwright E2E).
2. **Phase C (Docker Production Readiness)**:
   - Update `Dockerfile` to support dynamic `${PORT:-8000}` for Render compatibility.
   - Build local candidate Docker image and run containerized smoke tests verifying frontend delivery, API response, and healthchecks.
3. **Phase D (CI/CD Completion)**:
   - Verify all jobs in `.github/workflows/ci-cd.yml` pass on the consolidated codebase.
4. **Phase E & F (Conflict Resolution & Production Deployment)**:
   - Perform and record controlled merge conflict in `docs/final-project/MERGE_CONFLICT_EVIDENCE.md`.
   - Request human approval to promote `develop` to `main`.
   - Trigger production release on `main` to build, publish to Docker Hub, and deploy to Render.
5. **Phase G & H (Final Acceptance & Documentation)**:
   - Verify public HTTPS application, PvP/PvAI gameplay, and PostgreSQL persistence across restarts.
   - Produce comprehensive `README.md` and `FINAL_ACCEPTANCE_REPORT.md`.

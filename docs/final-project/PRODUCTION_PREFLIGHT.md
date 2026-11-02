# CaroAI — Production Preflight Audit & Deployment Guide

**Role:** Senior Software Architect, Tech Lead, DevOps Engineer, QA Lead
**Date:** November 2, 2026
**Repository:** `emt0147t/caroAI` (`D:\caro-ai\caroAI`)
**Integration Branch:** `develop`
**Verified Commit SHA:** `f796ef923a9d39e398139f0c540186a3ebb8a633`
**Production Branch Baseline:** `main` (`d444119d5eb757e364f904bb9eacddd27e14e507`)
**Verified CI Workflow Run:** GitHub Actions Run [#41470234191](https://github.com/emt0147t/caroAI/actions/runs/41470234191) on `f796ef9` (`status: completed`, `conclusion: success`)
**Historical PR #49 Baseline:** PR #49 merged at `6cf9bf08b8fb374645b7ecf79eb7a886ac002ef6` (CI Run [#41462195364](https://github.com/emt0147t/caroAI/actions/runs/41462195364))

---

## 1. Repository Baseline & Git State

| Parameter | Current Audited Value | Status |
|---|---|---|
| **Current Branch** | `develop` | Aligned with `origin/develop` |
| **Current Commit SHA** | `f796ef923a9d39e398139f0c540186a3ebb8a633` | Verified on remote |
| **Remote Branch SHA** | `f796ef923a9d39e398139f0c540186a3ebb8a633` | In exact sync |
| **Working Tree Status** | Clean (tracked changes audited) | Zero uncommitted external files |
| **Main / Develop Relationship** | `develop` is 387 commits ahead, 0 behind `main` | 338 non-merge commits, 49 merge commits; strictly linear ancestry |
| **Backup Branch** | `backup/develop-before-pr49-sync-20261102` (`5326543`) | Preserved safely |
| **Ruleset Configuration** | `CaroAI - Protect Develop` allows direct push; `Restrict deletions` and `Block force pushes` remain enabled | Routine engineering proceeds direct-to-develop; `main` requires PR + 1 approval |
| **Latest Verified CI Run** | Run [#41470234191](https://github.com/emt0147t/caroAI/actions/runs/41470234191) on commit `f796ef9` | All 6 test/build jobs succeeded; release skipped as expected |

---

## 2. Application Architecture Verification

### 2.1 Component Breakdown & Verification Level

| Component | Code / Local Implementation | Verification Level | Operational Behavior |
|---|---|---|---|
| **FastAPI Backend** | `app/main.py`, `app/api/*` | **Code-verified & Locally tested** | REST endpoints (`/api/games`, `/api/history`, `/health`, `/ready`) enforce server-side game rules, move validation, and turn alternation. |
| **Static Frontend Serving** | Mounted at `/` in `app/main.py` | **Code-verified & Locally tested** | Serves `frontend/Caro_AI/` (`welcome.html`, `trong_tran/index.html`, `tokens.css`) from the same container on port `${PORT:-8000}`. Root `/` serves modern dashboard. |
| **PostgreSQL Persistence** | `app/db/database.py`, `app/db/repositories/*` | **Code-verified & CI-verified** | SQLAlchemy session factory bound to lazily initialized engine with `pool_pre_ping=True`. Persists game states and moves across container restarts. |
| **Database Migrations** | `scripts/migrate_database.py` | **Code-verified & CI-verified** | Explicit versioned SQL files (`000_initial_schema.sql`, `001_games_public_id.sql`) applied in transaction before Uvicorn starts; tracked in `schema_migrations`. |
| **Liveness & Readiness Probes** | `app/api/routes_health.py` | **Code-verified & CI-verified** | `/health` returns `{"status":"ok"}`. `/ready` executes database `SELECT 1` and returns 503 if unreachable. |
| **Containerization** | `Dockerfile`, `docker-compose.yml` | **Code-verified & Locally tested** | Multi-stage build (`python:3.11-slim`), non-root `appuser` (UID 10001), parameterized dynamic port `${PORT:-8000}`, signal-forwarding `exec` startup. |
| **Production Live Instance** | Render Web Service & Render PostgreSQL | **NOT PROVISIONED — NOT RUN** | Cloud infrastructure has not yet been provisioned; zero live production claims. |

---

## 3. Environment Variable Inventory & Cross-Check

Comprehensive cross-check across application source code, Dockerfile, Docker Compose, and CI workflow:

### 3.1 Runtime Environment Variables (Application Code)
| Variable Name | Reading Location | Purpose & Behavior | Default / Production Requirement |
|---|---|---|---|
| **`DATABASE_URL`** | `app/db/database.py`<br>`scripts/migrate_database.py` | Authoritative PostgreSQL connection string. `normalize_database_url()` converts `postgres://` or `postgresql://` prefixes to `postgresql+psycopg2://`. | **Required** in production. Raises `RuntimeError` if missing when DB operations are invoked. |
| **`PORT`** | `Dockerfile` | Container listening port for Uvicorn server and Docker `HEALTHCHECK`. Injected by Render runtime. | Defaults to `8000` via `${PORT:-8000}`. |

### 3.2 Test-Only Environment Variables (Fail-Closed Guards)
| Variable Name | Reading Location | Purpose |
|---|---|---|
| **`CAROAI_TEST_POSTGRES_ALLOWLIST`** | `app/db/testing.py` | Comma-separated `host:port/database` allowlist required before test DDL can execute. |
| **`TEST_DATABASE_URL`** | `tests/test_database_postgres.py`<br>`tests/postgres_suite.py` | Dedicated test PostgreSQL URL. |
| **`CAROAI_TEST_DATABASE_CONFIRMED`** | `tests/test_database_postgres.py`<br>`tests/postgres_suite.py` | Token (`disposable-test-database`) confirming target database is disposable. |

### 3.3 Tooling Environment Variables
| Variable Name | Reading Location | Purpose |
|---|---|---|
| **`CAROAI_SOURCE_SHA`** | `scripts/benchmark_ai_sprint3.py` | Annotates AI benchmark reports with source commit SHA. |

### 3.4 Local Docker Compose Orchestration Variables (Not Read by Python Code)
- `POSTGRES_DB`: Interpolates database name for local Postgres container.
- `POSTGRES_USER`: Interpolates username for local Postgres container.
- `POSTGRES_PASSWORD`: Interpolates password for local Postgres container.
- `POSTGRES_PORT`: Host port mapping for local Postgres (default: 5432).
- `APP_PORT`: Host port mapping for local backend (default: 8000).
- `APP_ENV`: Informational environment tag passed in Compose.
- `FRONTEND_PORT`: Host port mapping for local Nginx (default: 8080).

*No secrets, passwords, or connection strings are printed or committed.*

---

## 4. Docker Hub & Container Image Preflight

| Attribute | Specification | Verification Status |
|---|---|---|
| **Build Architecture** | Multi-stage `python:3.11-slim` | **Locally tested & CI verified** (`caroai:candidate`) |
| **Target Platform** | `platforms: linux/amd64` | **Configured in `.github/workflows/ci-cd.yml`** |
| **Runtime User** | `appuser` (UID 10001, GID 10001) | Non-root runtime enforced in `Dockerfile` |
| **Port Handling** | `ENV PORT=8000`, `--port ${PORT:-8000}` | Dynamically accepts Render port injection |
| **Context Hygiene** | `.dockerignore` excludes `.env*`, `.git`, `.github`, `docs/`, `venv/` | Zero secrets or extraneous files in image layers |
| **Tagging Scheme** | Full Commit SHA: `${IMAGE_NAME}:${GITHUB_SHA}`<br>Short SHA: `${IMAGE_NAME}:${GITHUB_SHA:0:12}` | Traceable commit-pinned tags (Full SHA is primary release reference; registry-side tag immutability is not asserted unless configured on Docker Hub) |
| **Digest Tracking** | Output digest captured via `${{ steps.publish.outputs.digest }}` | Cryptographic content identifier recorded in release step and exported to `$GITHUB_STEP_SUMMARY` |
| **Registry Publishing** | Push to `docker.io/${DOCKERHUB_USERNAME}/caroai` | **CONFIGURED — NOT RUN** (Pending owner credentials) |

---

## 5. Render Web Service & Database Preflight

### 5.1 Render Web Service
- **Service Model:** Image-backed Docker Web Service pulling from Docker Hub (`${IMAGE_NAME}:${GITHUB_SHA}`).
- **Health Check Path:** `/ready` (guarantees database connectivity and migration completion before traffic routing).
- **Auto-Deploy:** Must be set to **No** (disabled). Releases are driven exclusively by the GitHub Actions release workflow.
- **Deploy Hook:** Enabled on Render; URL provided to GitHub secret `RENDER_DEPLOY_HOOK`.
- **Deploy Verification:** Release workflow polls Render Deploy API (`https://api.render.com/v1/services/$RENDER_SERVICE_ID/deploys/$DEPLOY_ID`) until status is `live` AND image reference matches the exact requested SHA.
- **Downtime Management:** Render zero-downtime deploy is a platform capability designed to boot the new container, validate `/ready`, drain the old container with SIGTERM, and cut over traffic. Note: This behavior is conditional (subject to single-container limits and persistent-disk attachment constraints), and zero-downtime cutover has NOT been empirically tested or verified for this application on production.

### 5.2 Render Managed PostgreSQL
- **Connection URL Preference:** Render provides an **Internal Database URL** (e.g. `postgresql://caroai_user:...@dpg-...-a/caroai_db`) and an External Database URL.
  - The Web Service must use the **Internal Database URL** when deployed in the same region/account (lower latency, private network isolation, zero bandwidth costs).
- **TLS / SSL Policy:**
  - Internal connections within the private Render network support TLS; application relies on `psycopg2-binary` default negotiation.
  - External connections enforce TLS encryption (`sslmode=require`); unencrypted `sslmode=disable` is prohibited.
- **Storage & Durability:** Render PostgreSQL provisions persistent block storage according to the selected plan tier (Free/Starter/Standard). Data persists across application container restarts and redeployments.

---

## 6. Production Read-Only Smoke Tests

The post-deployment verification in `.github/workflows/ci-cd.yml` executes read-only HTTP GET smoke tests across all core application routes:

| Target Endpoint | Description | Expected HTTP Status | Verification Focus |
|---|---|---|---|
| **`GET /health`** | Liveness probe | `200 OK` | Fast-path application process availability. |
| **`GET /ready`** | Database readiness probe | `200 OK` | Database connection pool active; `SELECT 1` succeeds. Returns 503 if DB is unreachable. |
| **`GET /`** | Root UI dashboard | `200 OK` | Static file serving active; loads `welcome.html` gaming hub. |
| **`GET /history.html`** | History UI page | `200 OK` | Historical matches browser UI asset availability. |
| **`GET /api/history`** | History REST API | `200 OK` | REST API routing and JSON response serialization from PostgreSQL. |
| **`GET /tokens.css`** | Design tokens | `200 OK` | Static CSS stylesheet asset serving. |

### Smoke Test Design Principles:
1. **HTTP GET Only:** Strictly read-only; does not create games, make moves, or modify database records.
2. **Exponential / Retry Loop:** Up to 12 attempts with 5-second intervals (60-second window) to accommodate warm-up.
3. **Transparent Logging:** Outputs requested path, description, HTTP status code, and attempt count.
4. **Zero Credential Exposure:** Secrets and authorization headers are never logged or echoed.
5. **Fail-Closed:** Any endpoint failing after 12 retries aborts the workflow with non-zero exit code.

---

## 7. GitHub Production Environment Preflight

Configuration required in repository settings (**Settings** → **Environments** → **`production`**):

| Secret / Variable Name | Type | Current Status | Operational Role |
|---|---|---|---|
| **`DOCKERHUB_USERNAME`** | Secret | **Not yet configured** | Docker Hub account username for registry login. |
| **`DOCKERHUB_TOKEN`** | Secret | **Not yet configured** | Personal Access Token with Read/Write registry scope. |
| **`RENDER_DEPLOY_HOOK`** | Secret | **Not yet configured** | Render Web Service Deploy Hook URL. |
| **`RENDER_API_KEY`** | Secret | **Not yet configured** | Personal API key for polling Render deploy status API. |
| **`RENDER_SERVICE_ID`** | Secret | **Not yet configured** | Service identifier (`srv-...`) from Render Web Service. |
| **`CAROAI_PUBLIC_URL`** | Variable | **Not yet configured** | Public HTTPS URL (e.g. `https://<service-name>.onrender.com`). |

*Status note: Environment credentials have not been configured or tested in production. No secret values are stored in repository files.*

### 7.1 Environment Protection & Approval Gate Review
- **Environment Approval Gate:** While `.github/workflows/ci-cd.yml` references `environment: name: production`, GitHub Actions does NOT enforce manual approvals unless configured by the repository owner. Required Reviewers setting: **NOT VERIFIED — owner action required** under **Settings → Environments → `production`**.
- **Deployment Branch Policy:** Environment deployment branch rules must be explicitly configured to restrict deployments exclusively to `main` (preventing unauthorized branches from triggering production actions). Status: **NOT VERIFIED — owner action required**.

---

## 8. Release Sequence & Promotion Flow

```mermaid
sequenceDiagram
    autonumber
    actor Owner as Tech Lead / Owner
    actor Reviewer as Write-Access Reviewer
    participant GitHub as GitHub (develop & main)
    participant CI as GitHub Actions
    participant Hub as Docker Hub
    participant Render as Render Cloud

    Note over Owner,GitHub: Step 1: Local & CI validation complete on develop (f796ef9)
    Owner->>Render: Step 2: Provision PostgreSQL (caroai_db) & Web Service
    Owner->>GitHub: Step 3: Populate Environment "production" secrets & variables
    Owner->>GitHub: Step 4: Open Pull Request from develop into main
    Reviewer->>GitHub: Step 5: Review and approve PR into main
    Owner->>GitHub: Step 6: Merge PR into main
    Owner->>CI: Step 7: Dispatch "CaroAI CI" on main (release_approved=true)
    CI->>CI: Step 8: Execute test gates & validate secrets
    CI->>Hub: Step 9: Build & push image (linux/amd64, full SHA + short SHA, digest tracked)
    CI->>Render: Step 10: Call Deploy Hook with imgURL=<IMAGE>:<FULL_SHA>
    Render->>Hub: Step 11: Pull image & run migrations
    Render->>Render: Step 12: Launch Uvicorn on $PORT
    CI->>Render: Step 13: Poll Deploy API until status=live & exact SHA confirmed
    CI->>Render: Step 14: Run GET-only smoke tests (/health, /ready, /, /history.html, /api/history, /tokens.css)
    CI-->>Owner: Step 15: Release verified & live!
```

### 8.1 Promotion Rules & Branch Gating
Direct push to `main` is strictly prohibited by repository rulesets (`main` enforces Pull Request reviews with at least 1 approval). Promotion from `develop` to `main` must follow the formal Pull Request sequence:
1. Open a Pull Request from `develop` to `main`.
2. A write-access team member reviews and submits an approving review.
3. The PR is merged into `main`.
4. Triggering the production release is a separate subsequent manual action via `workflow_dispatch` on `main` with `release_approved=true`.

---

## 9. Rollback & Disaster Recovery Procedures

1. **Instant Cloud Rollback (Render Dashboard):**
   - Navigate to Render Web Service → **Deploys**.
   - Select the previously healthy deployment and click **Rollback to this deploy**.
   - Render immediately points traffic to the previous Docker container image.
2. **Git Rollback:**
   - Revert the offending commit on `develop`, verify tests, promote to `main` via Pull Request and review approval, and re-dispatch the release workflow.
3. **Database Schema Backward Compatibility:**
   - Migrations are strictly additive (`CREATE TABLE IF NOT EXISTS`, `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`). Previous application images remain fully compatible with the schema.

---

## 10. Remaining Blockers Prior to Production

1. **Cloud Provisioning:** Render Web Service and Render Managed PostgreSQL must be provisioned under owner account.
2. **GitHub Environment Secrets:** The 5 secrets and 1 variable in Environment `production` must be populated.
3. **Main Branch Promotion:** A Pull Request from `develop` (`f796ef9`) into `main` must be opened, approved by a reviewer, and merged prior to triggering the production release workflow on `main`. Direct push to `main` is prohibited by branch protection rules.

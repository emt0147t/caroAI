# CaroAI — Final Project Acceptance Report

**Project**: CaroAI — 15×15 Gomoku AI Application
**Repository**: `emt0147t/caroAI`
**Evaluation Role**: Principal Software Engineer + Tech Lead + DevOps Engineer + QA Lead
**Assessment Date**: November 7, 2026 (current-status addendum; historical audit evidence retained below)
**Integration Branch**: `develop` (current synchronized baseline: `42ee035ab42cd4c0bc934699f4d5433ff4b12a83`)
**Production Branch**: `main` (current production baseline: `42ee035ab42cd4c0bc934699f4d5433ff4b12a83`)
**Delivery PR Status**: PR #58 has been merged to `main`; current `main` and `develop` are identical at `42ee035ab42cd4c0bc934699f4d5433ff4b12a83`. The current production release is live via Render deployment `dep-dbn02vrncjis73am3dhg`.

---

## 0. Current Release and Engineering Status — 2026-11-07 (Authoritative)

This section supersedes conflicting release, branch, and deployment statements in the historical November 3 audit sections below. Older sections are retained as provenance for the original university-project acceptance review; they are not the current release state.

### Current Git and production baseline

| Item | Verified value |
|---|---|
| `main` | `42ee035ab42cd4c0bc934699f4d5433ff4b12a83` |
| `develop` | `42ee035ab42cd4c0bc934699f4d5433ff4b12a83` |
| Branch comparison | Identical; 0 ahead / 0 behind |
| Production service | Render `srv-dbkd2dflk1mc73fd2ukg` |
| Production deployment | `dep-dbn02vrncjis73am3dhg`, status `live` |
| Production image | `docker.io/emt0147/caroai:42ee035ab42cd4c0bc934699f4d5433ff4b12a83` |
| Image digest | `sha256:a80c48d0f1433f600ef5d5e2a5dc124f3057cebe716ab9782f238a614f7f35a7` |
| Production URL | [https://caroai-bootstrap-a9e753b33198.onrender.com](https://caroai-bootstrap-a9e753b33198.onrender.com) |
| Release workflow | [Run #42253079008](https://github.com/emt0147t/caroAI/actions/runs/42253079008), success |

### Current verification evidence

| Verification | Result | Scope / qualification |
|---|---|---|
| Production release and exact image verification | PASS | Render reports the exact commit-SHA image as live |
| Public release smoke checks | 6 endpoints HTTP 200 | `/health`, `/ready`, `/`, `/history.html`, `/api/history`, `/tokens.css` |
| Release CI | PASS | Python suite 253 passed, 11 skipped, 1 warning; dedicated PostgreSQL acceptance 15 passed; Compose persistence and Docker build passed |
| Browser E2E | PASS, 40 tests | Candidate/Compose environment in [run #42241696370](https://github.com/emt0147t/caroAI/actions/runs/42241696370), not a post-deploy production-browser run |
| Phase C controlled Minimax benchmark | PASS | 1,320 measured calls, 0 failures; [run #42267880120](https://github.com/emt0147t/caroAI/actions/runs/42267880120) |
| Phase C API/PostgreSQL benchmark | PASS | Disposable PostgreSQL 15.19; 721 correctness checks, 0 failures; [run #42267879898](https://github.com/emt0147t/caroAI/actions/runs/42267879898) |
| Phase C CI and browser E2E | PASS | [CI #42267890333](https://github.com/emt0147t/caroAI/actions/runs/42267890333); [Browser E2E #42267890323](https://github.com/emt0147t/caroAI/actions/runs/42267890323); production release job skipped |

### Current outstanding acceptance work

1. **Documentation:** current-state refresh for README, this report, Production Preflight, and benchmark report is included in this documentation PR; merge is pending review.
2. **Phase C integration:** Phase C code is on feature branch `feat/phase-c-ai-observability-qa-20261106`, tested at source SHA `8ca52e0ed4a5a2ba4546f94978dcb0c1fb06339f`. It has not been merged to `main` or deployed. Review and PR acceptance remain required.
3. **Production gameplay acceptance:** the Phase C run-scoped PvP/PvAI QA runner has not been executed against the live website because its QA routes and migration are not deployed. Do not claim post-Phase-C production PvP/PvAI acceptance yet.
4. **Observability:** Phase C Prometheus instrumentation and alert rules are feature-branch code; a scraper/Alertmanager/notification destination is not configured. Render provider metrics returned CPU/memory samples but no HTTP latency/request-count series in the queried window.
5. **Performance objective:** 2,000 ms remains a proposed reference, not an adopted production SLO. Hosted-runner benchmarks do not establish production traffic percentiles.

---

## 1. Project Overview & System Scope

CaroAI is a university Final Project delivering a full-stack, 15×15 Gomoku (Cờ Caro) AI gaming platform. The application enforces absolute server-side authority:
- Client code in HTML5/CSS3/JavaScript captures user inputs and renders visual state.
- The FastAPI backend validates coordinates, enforces turn alternation, tracks moves, calculates 5-in-a-row win and draw states, and invokes the Python Minimax AI engine with Alpha-Beta pruning.
- Game and move states are persisted atomically to PostgreSQL.
- The runtime is containerized using a multi-stage Dockerfile serving both the static frontend and REST API on the dynamic port assigned by Render (`${PORT:-8000}`).

---

## 2. University Final Project Requirements Acceptance Matrix

| Requirement | Acceptance Criteria | Truthful Status | Evidence & Test Results | Source SHA / Ref | Outstanding Limitations |
|---|---|---|---|---|---|
| **Git Commits (>= 30)** | At least 30 meaningful commits in repository history | **PASS** | `origin/main..938a174` yields **388 commits** (339 non-merge, 49 merge commits). Core implementation and engineering commits alone total **159 commits**. | `origin/develop` (Baseline `938a174`) | None. Exceeds requirement by >5x for implementation commits and >12x overall. |
| **Five-Member Collaboration** | Demonstrable contribution across all 5 team members | **PASS** | Exact shortlog on non-merges (N=339): Vũ Duy Hiếu (142 commits, 41.9%), Nguyễn Xuân Thành (86 commits, 25.4%), Mạc Quang Vinh (51 commits, 15.0%), Ngọc Hiền (41 commits, 12.1%), Trần Danh Kiên (19 commits, 5.6%). Sums exactly to 339 non-merge commits (100.0%). | `docs/final-project/GIT_COLLABORATION_AUDIT.md` (Baseline `938a174`) | None. Preserved in Git commit graph without squashing or history rewriting. |
| **Feature Branches & PRs** | Clean branch workflow, PR reviews, branch protection | **PASS** | PR #58 integrated the Impossible difficulty and benchmark updates into `main`; current `main` and `develop` are synchronized at `42ee035`. Historical PR #50 references below describe the earlier promotion cycle and are superseded by PR #58. | [PR #58](https://github.com/emt0147t/caroAI/pull/58) | Historical documentation PRs require separate backlog review. |
| **Merge Conflict Resolution** | Genuine conflict created, resolved, tested, and documented | **PASS** | Competing branches `feature/deploy-config-resources` (`8fe6c02`) and `feature/deploy-config-networking` (`30530b7`) conflicted on `docs/final-project/deployment-config.md`. Resolved into `67bdf86`. | `67bdf86` | None. Documented with unified diffs and markers in `MERGE_CONFLICT_EVIDENCE.md`. |
| **Multi-Stage Dockerfile** | Non-root user, dynamic port `${PORT:-8000}`, healthcheck | **PASS** | Built candidate image `caroai:candidate` (`sha256:630fe329...`). Unified container serves both static UI and API on same port. Healthcheck validates `http://localhost:${PORT:-8000}/ready`. | `Dockerfile` | None. Verified locally and via CI check `Docker image build`. |
| **Docker Hub Publishing** | Automated release job publishes full-SHA and short-SHA tags to Docker Hub | **LIVE / VERIFIED** | Production release workflow #42253079008 published the commit-pinned image `docker.io/emt0147/caroai:42ee035ab42cd4c0bc934699f4d5433ff4b12a83`; Render reports the matching image digest as live. | [Production release run](https://github.com/emt0147t/caroAI/actions/runs/42253079008) | Release evidence is specific to this SHA; future releases still require an approved manual dispatch. |
| **GitHub Actions CI/CD** | Automated pipeline: Test → Lint → DB Acceptance → Compose Smoke → Secret Scan → Build → gated release | **PASS** | Current production release succeeded in run #42253079008. Release candidate CI reported 253 passed, 11 skipped, 1 warning; dedicated PostgreSQL acceptance 15 passed; Compose persistence, secret scan, Docker build and browser E2E passed. | [Release run #42253079008](https://github.com/emt0147t/caroAI/actions/runs/42253079008) | Phase C branch verification is separate; its release job was intentionally skipped. |
| **PostgreSQL Persistence** | Authoritative persistence surviving app restart | **PASS (CI / PostgreSQL acceptance)** | Dedicated PostgreSQL acceptance passed 15/15; Compose verified PvP/PvAI, AI move, history and persistence after API restart. Earlier live-cloud persistence verification is retained as historical evidence; no new production restart test was performed for this release. | [Release run #42253079008](https://github.com/emt0147t/caroAI/actions/runs/42253079008) | Re-run live durability acceptance if a production restart/migration changes. |
| **Public HTTPS Address** | Publicly accessible URL on Render with live game | **PRODUCTION LIVE / ENDPOINTS VERIFIED** | Render deployment `dep-dbn02vrncjis73am3dhg` runs exact image SHA `42ee035...`; release smoke checks returned HTTP 200 for `/health`, `/ready`, `/`, `/history.html`, `/api/history`, and `/tokens.css`. | [Live website](https://caroai-bootstrap-a9e753b33198.onrender.com) · [Release run](https://github.com/emt0147t/caroAI/actions/runs/42253079008) | Full interactive PvP/PvAI acceptance on the live site remains a separate outstanding test. |
| **Comprehensive Technical Documentation** | Full README, setup guide, architecture, testing, API docs | **PASS** | `README.md` updated with all 20 required sections. Full audits in `docs/final-project/`: `PRODUCTION_PREFLIGHT.md`, `GIT_COLLABORATION_AUDIT.md`, `FINAL_ACCEPTANCE_REPORT.md`, `PHASE_A_REPOSITORY_AUDIT.md`, `MERGE_CONFLICT_EVIDENCE.md`, `deployment-config.md`. | `README.md` | None. |

---

## 3. Audit Baseline (`938a174`) Verification Evidence

### 3.1 GitHub Actions Check Runs for Baseline `938a174`
All core verification jobs executed against commit `938a17408078ca58c9bec6bf42eec09758be6165` in GitHub Actions Run [#41475666768](https://github.com/emt0147t/caroAI/actions/runs/41475666768) and completed successfully:

| Check Run Name | Status | Conclusion | Notes |
|---|---|---|---|
| **Python tests and lint** | Completed | **success** | flake8 (0 errors), pytest (242 passed, 11 skipped) |
| **PostgreSQL service/API/migration acceptance** | Completed | **success** | 15/15 passed against ephemeral PostgreSQL 15 service |
| **Frontend syntax and regression checks** | Completed | **success** | node --check, 7 node regression tests passed |
| **Compose API/database persistence after restart** | Completed | **success** | Docker Compose persistence verified after restart |
| **Secret scan (PR diff and full Git history)** | Completed | **success** | Gitleaks scanned 0 secrets |
| **Docker image build (no publish/deploy)** | Completed | **success** | Candidate image `caroai:candidate` built successfully |
| **Approved production publish and Render verification** | Completed | **skipped** | Gated for `main` release path with `release_approved=true` |

> [!NOTE]
> **Playwright Browser E2E Provenance:** The 28 Playwright browser E2E tests are configured in dedicated workflow `.github/workflows/frontend-e2e.yml` and ran successfully in GitHub Actions Run [#41460505248](https://github.com/emt0147t/caroAI/actions/runs/41460505248) (commit `734a90b`), as well as in local pre-commit verification (`npm run test:e2e`, 28 passed, 0 failed, 24.6s). They are not part of Run #41475666768, which executed the core `ci-cd.yml` workflow.

### 3.2 Latest PR-Triggered CI Run Before Documentation Refresh — #41570710412 (PR #50 on `7f74221`)
Pull Request #50 triggered GitHub Actions Run [#41570710412](https://github.com/emt0147t/caroAI/actions/runs/41570710412) against verified commit `7f7422123654fa6f6293cde3d15c2a6057bc6b92`:
- **Workflow:** CaroAI CI/CD (`ci-cd.yml`)
- **Event:** `pull_request` (targeting `main`)
- **Status:** Completed (`conclusion: success`)
- **Job Results:**
  - **Python tests and lint** — `success` (flake8: 0 errors; pytest: 242 passed, 11 skipped; one Starlette/httpx deprecation warning)
  - **Frontend syntax and regression checks** — `success` (`node --check` passed; 7 regression tests passed)
  - **PostgreSQL service/API/migration acceptance** — `success` (15/15 passed; zero skipped in the dedicated PostgreSQL acceptance suite)
  - **Compose API/database persistence after restart** — `success` (PvP, PvAI, AI move, history, and persistence after app restart passed)
  - **Secret scan (PR diff and full Git history)** — `success` (both Gitleaks steps completed successfully)
  - **Docker image build (no publish/deploy)** — `success` (candidate image build completed)
  - **Approved production publish and Render verification** — `skipped intentionally` (release job gated for authorized `main` dispatch)

### 3.3 Historical PR CI Run #41502411622 Evidence (PR #50 on `2a46000`)
Pull Request #50 previously executed GitHub Actions Run [#41502411622](https://github.com/emt0147t/caroAI/actions/runs/41502411622) against pre-hardening develop snapshot `2a46000b455f9b9779fd7289c6b22ae080aaa44c`, serving as historical pre-hardening verification evidence.

### 3.4 Live Cloud Bootstrap Deployment & Persistence Evidence
The live cloud bootstrap deployment was provisioned and comprehensively validated:
- **Docker Hub Image:** `docker.io/emt0147/caroai:bootstrap-a9e753b33198` (manually published by repository owner `emt0147`).
- **Render Web Service:**
  - Service ID: `srv-dbkd2dflk1mc73fd2ukg`
  - Instance Type: Free
  - Public URL: `https://caroai-bootstrap-a9e753b33198.onrender.com`
  - Health check path: `/ready`
- **Neon Serverless PostgreSQL:**
  - Project: `caroai-demo`
  - Region: AWS Singapore (`ap-southeast-1`)
  - Plan: Free
  - PostgreSQL Version: 18
  - Database Name: `neondb`
  - Branch: `production`
  - Connection Mode: Direct (non-pooler) connection with `sslmode=require` and `channel_binding=require`. `DATABASE_URL` configured in Render environment settings (raw credentials never documented).
- **Startup Migrations:** Render startup logs confirmed migrations `000_initial_schema.sql` and `001_games_public_id.sql` applied successfully; schema up to date.
- **Endpoint Verification (HTTP 200 OK):**
  - `GET /health`: HTTP 200 `{"status":"ok"}`
  - `GET /ready`: HTTP 200 `{"status":"ready","database":"ok"}`
  - `GET /`: HTTP 200 (Dashboard UI loaded)
  - `GET /history.html`: HTTP 200 (History UI loaded)
  - `GET /api/history`: HTTP 200 (Matches array JSON)
  - `GET /tokens.css`: HTTP 200 (Design tokens stylesheet)
- **Live Gameplay Verification:**
  - PvP mode: Match initialized, moves registered, and victory condition evaluated.
  - PvAI mode: Match initialized, human moves accepted, AI engine calculated and returned player O moves.
  - History retrieval: Game details, timestamps, and move lists retrievable via `/api/history`.
- **Post-Restart Persistence Verification:**
  - Render Web Service restart executed.
  - Following container restart, both PvP and PvAI games and histories remained completely intact and retrievable.
  - **Verdict:** `POST-RESTART PERSISTENCE: PASS`.

### 3.5 Local Test Execution & Final Container Filesystem Inspection Evidence

| Test Suite | Command | Total Tests / Metrics | Result | Duration |
|---|---|---|---|---|
| **Python Code Quality** | `py -3.11 -m flake8 app tests scripts --count --max-complexity=10 --max-line-length=127 --statistics` | 0 lint errors | **PASS** | 1.1s |
| **Python Unit & API Suite** | `py -3.11 -m pytest -q tests/` | 242 passed, 11 skipped | **PASS** | 4.7s |
| **Dedicated PostgreSQL Suite** | `py -3.11 -m pytest -q tests/test_database_postgres.py tests/postgres_suite.py` | 15 passed, 0 skipped | **PASS** | 3.3s |
| **Frontend Syntax** | `node --check frontend/Caro_AI/trong_tran/script.js` | 0 syntax errors | **PASS** | 0.1s |
| **Frontend Regression** | `node --test tests/frontend-regression.test.cjs` | 7 passed, 0 failed | **PASS** | 0.1s |
| **Playwright Browser E2E** | `npm run test:e2e` | 28 passed, 0 failed | **PASS** | 24.6s |
| **Docker Compose Config** | `docker compose config --quiet` | 0 errors | **PASS** | 0.4s |
| **Git Working Tree Check** | `git diff --check` | 0 errors | **PASS** | Clean |
| **All 8 API Endpoints** | Live audit against running backend container | All 8 endpoints 200/201 OK | **PASS** | Clean |
| **Container Persistence** | State preserved after `docker restart caroai-backend` | `GET /api/games/{id}` 200 OK | **PASS** | Clean |

#### Final Container Filesystem Inspection Evidence
A final container filesystem inspection was performed against review image `caroai:premerge-review`:
- **Image**: `caroai:premerge-review`
- **Image ID**: `sha256:270e19a83a4aecc6e94fc0d90800ce562184b394c0b10cc6836362d9093c11a5`
- **Inspection Command**:
  ```bash
  docker run --rm --entrypoint sh caroai:premerge-review -c "id; echo '--- ENV FILE CHECK ---'; find /app -type f \( -name '.env' -o -name '.env.*' \) -print"
  ```
- **Observed Inspection Output**:
  - Runtime identity: `uid=10001(appuser) gid=10001(appuser)`.
  - Environment template: `/app/.env.example` present.
  - Secret file check: No `.env`, `.env.local`, or `.env.production` files found under `/app`.
- **Inspection Scope & Precision Note**:
  - This is a final container filesystem inspection of the review image.
  - It is not a complete scan of all historical image layers.
  - Gitleaks full Git-history scanning is a separate CI check.
  - No claim is made that all historical image layers have been independently scanned.

---

## 4. Pull Request #49 Integration & Branch Ruleset Transition

### 4.1 PR #49 Integration, PR #50 Status & Open PR Inventory
- **PR #49 (Final Delivery PR)**: [PR #49](https://github.com/emt0147t/caroAI/pull/49) (`feature/final-project-delivery` → `develop`, Head SHA: `b22e0bd597f858be6777d7e4b8685a56c04521c2`) was officially merged into `develop` via merge commit `6cf9bf08b8fb374645b7ecf79eb7a886ac002ef6`.
- **PR #50 (Production Promotion PR)**: Pull Request #50 (`develop` → `main`) promotes verified engineering to `main`. Latest CI-verified pre-refresh snapshot was `7f7422123654fa6f6293cde3d15c2a6057bc6b92` (CI Run [#41570710412](https://github.com/emt0147t/caroAI/actions/runs/41570710412) passed). Earlier snapshots: `caf9d92` (Run #41565255360) and historical pre-hardening `2a46000` (Run #41502411622). The current PR head and any subsequent documentation-only refresh are tracked live on [PR #50](https://github.com/emt0147t/caroAI/pull/50).
- **Open Pull Requests (4 PRs)**:
  - **PR #50**: Active pre-merge PR from `develop` into `main`.
  - **PR #25**: `docs: add Sprint 3 phase 3 team execution plan` (created 2026-10-16 by `emt0147t`)
  - **PR #26**: `docs: record Sprint 2 closeout and Sprint 3 handover status` (created 2026-10-16 by `emt0147t`)
  - **PR #27**: `docs: define detailed Sprint 3 assignments and release gates` (created 2026-10-16 by `emt0147t`)
  *(Note: PRs #25, #26, #27 represent historical Sprint 3 planning proposals that were superseded by subsequent sprint execution and remain open in the repository; they are not actively maintained).*

### 4.2 Historical Direct Push Blocker (GH013) & Resolution
- **Historical Blocker:** Prior to merge, GitHub branch protection on `develop` enforced rule `GH013` requiring at least 1 approving review from write-access collaborators, preventing unapproved direct pushes.
- **Ruleset Adjustment:** To support routine post-delivery maintenance and preflight audits, the repository owner updated the `CaroAI - Protect Develop` ruleset to remove the pull request requirement, permitting direct pushes to `develop`. Protection against branch deletion (`Restrict deletions`) and force-pushing (`Block force pushes`) remains actively enforced.
- **Verification of Direct Push:** Direct push to `develop` was validated on commit `f796ef923a9d39e398139f0c540186a3ebb8a633` (CI Run #41470234191 passed).
- **Main Branch Ruleset Unchanged:** `main` remains protected by a strict Pull Request requirement and at least 1 approving review. Direct push to `main` is prohibited.

---

## 5. Production Rollout Status & Checklist

Infrastructure and release rollout status as of PR #50 pre-merge reconciliation:

1. **Cloud Bootstrap Deployment (Verified LIVE)**:
   - Render Web Service (`srv-dbkd2dflk1mc73fd2ukg`) is live at `https://caroai-bootstrap-a9e753b33198.onrender.com` using image `emt0147/caroai:bootstrap-a9e753b33198`.
   - Connected to Neon Serverless PostgreSQL (`caroai-demo`, AWS Singapore `ap-southeast-1`, `neondb`).
   - Migrations executed, API endpoints 200 OK, PvP/PvAI gameplay verified, and data persistence verified across service restart (`POST-RESTART PERSISTENCE: PASS`).
2. **GitHub Production Environment Secrets & Variables**:
   - The five production secrets (`DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `RENDER_DEPLOY_HOOK`, `RENDER_API_KEY`, `RENDER_SERVICE_ID`) are owner-reported entered under GitHub Settings → Environments → `production`, but have not yet been validated by an executing production release (release jobs skipped in CI).
   - **Environment Variable `CAROAI_PUBLIC_URL`**: Status is **UNCONFIRMED — PENDING OWNER VERIFICATION**. Do not claim it is configured or infer its presence from the five secrets.
3. **GitHub Production Environment Protections**:
   - Under Settings → Environments → `production`:
     - **Required reviewers**: Unconfirmed / awaiting verification (do not claim configured unless independently confirmed).
     - **Deployment branches**: Unconfirmed / awaiting verification (do not claim configured unless independently confirmed).
4. **Promote `develop` to `main` via Pull Request #50**:
   - Pull Request #50 (`develop` → `main`) is open.
   - Requires review approval from an authorized collaborator before merge.
   - *(Note: Direct push `git push origin main` is blocked by repository branch protection).*
5. **Trigger Official Production Release**:
   - Following merge of PR #50, trigger `CaroAI CI/CD` workflow on `main` via `workflow_dispatch` with `release_approved=true`.
   - The release job will build, tag, and publish official full-SHA and short-SHA images to Docker Hub (`emt0147/caroai`), trigger the Render Deploy Hook, poll the Render API until live, and verify public HTTPS endpoints.

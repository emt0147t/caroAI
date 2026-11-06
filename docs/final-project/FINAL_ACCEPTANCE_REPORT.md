# CaroAI — Final Project Acceptance Report (Current Release Snapshot)

**Project**: CaroAI — 15×15 Gomoku AI Application
**Repository**: `emt0147t/caroAI`
**Evaluation Role**: Principal Software Engineer + Tech Lead + DevOps Engineer + QA Lead
**Current Release Assessment Date**: November 6, 2026
**Current Production Source SHA**: `42ee035ab42cd4c0bc934699f4d5433ff4b12a83`
**Current Production Deploy**: `dep-dbn02vrncjis73am3dhg` (`live`)
**Current Release Workflow**: [GitHub Actions #605](https://github.com/emt0147t/caroAI/actions/runs/42253079008) (`workflow_dispatch`, `success`)

> **Current-state authority:** the checkpoint below supersedes historical “bootstrap only”, “official release pending”, and PR #50 pending statements in the archival sections that follow. Earlier audit baselines and their test counts remain historical evidence, not the current production state.
**Integration Branch**: `develop` (Audit Baseline Commit SHA: `938a17408078ca58c9bec6bf42eec09758be6165`, Historical Pre-Hardening Snapshot: `2a46000b455f9b9779fd7289c6b22ae080aaa44c`, Latest CI-Verified Pre-Refresh Snapshot: `7f7422123654fa6f6293cde3d15c2a6057bc6b92`; PR CI Run [#41570710412](https://github.com/emt0147t/caroAI/actions/runs/41570710412) completed successfully. The subsequent report refresh is documentation-only.)
**Production Branch**: `main` (Baseline SHA: `d444119d5eb757e364f904bb9eacddd27e14e507`)
**Delivery PR Status**: [Pull Request #49](https://github.com/emt0147t/caroAI/pull/49) (`feature/final-project-delivery` → `develop`) was successfully merged into `develop` via official merge commit `6cf9bf08b8fb374645b7ecf79eb7a886ac002ef6`. Direct pushes to `develop` succeeded at `f796ef9` and audit baseline `938a174` (CI Run [#41475666768](https://github.com/emt0147t/caroAI/actions/runs/41475666768) verified). PR #50 opened from `develop` targeting `main` (historical pre-hardening CI Run [#41502411622](https://github.com/emt0147t/caroAI/actions/runs/41502411622) on `2a46000`; intermediate CI Run [#41565255360](https://github.com/emt0147t/caroAI/actions/runs/41565255360) on `caf9d92`; latest CI-verified pre-refresh snapshot `7f74221` passed in Run [#41570710412](https://github.com/emt0147t/caroAI/actions/runs/41570710412)).

## Current Production Acceptance — 2026-11-06

| Gate | Current evidence | Result |
|---|---|---|
| Source promotion | `main` and `develop` both at `42ee035ab42cd4c0bc934699f4d5433ff4b12a83` after fast-forward of develop | PASS |
| Release authorization and build | [Workflow #605](https://github.com/emt0147t/caroAI/actions/runs/42253079008); production Environment configuration validated; full-SHA Docker image published | PASS |
| Render deploy | `dep-dbn02vrncjis73am3dhg`; exact image `docker.io/emt0147/caroai:42ee035ab42cd4c0bc934699f4d5433ff4b12a83`; status `live` | PASS |
| Production HTTP smoke | `/health`, `/ready`, `/`, `/history.html`, `/api/history`, `/tokens.css`: all HTTP 200 | PASS |
| Python suite | 253 passed, 11 skipped, 1 warning | PASS with skips disclosed |
| Dedicated PostgreSQL acceptance | 15 passed, zero skipped | PASS |
| Compose persistence | PvP, PvAI, AI move, detail/history, application restart persistence | PASS |
| Browser E2E / visual regression | Candidate run #176: 40 passed; visual comparison 12 baseline matches, 3 new evidence checks, 0 failures | PASS (candidate environment, not live production browser session) |

### Current limitations — not accepted as complete

- Phase A/Phase B benchmarks show high IMPOSSIBLE tail latency under concurrent requests; Phase C instrumentation and optimization are not yet part of this release.
- Production GET smoke does not constitute a full production PvP/PvAI end-to-end gameplay test.
- The Phase B API/PostgreSQL benchmark is a controlled Windows 10 / Python 3.11.9 / PostgreSQL 15.19 run with one API worker, not a Render production load test.
- Branches are synchronized at this checkpoint. Future changes must continue to follow the protected-main PR/review and manual release workflow.

---

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
| **Feature Branches & PRs** | Clean branch workflow, PR reviews, branch protection | **PASS** | 42 total Pull Requests across repository history. PR #49 reviewed and merged into `develop` (`6cf9bf0`). PR #50 opened targeting `main` from `develop` (latest CI-verified pre-refresh snapshot `7f74221`, CI Run #41570710412; intermediate snapshot `caf9d92`, CI Run #41565255360; historical pre-hardening snapshot `2a46000`, CI Run #41502411622). Note: 3 unmerged historical documentation PRs (#25, #26, #27) remain open from Sprint 3 planning. | PR #46, #47, #48, #49, PR #50 | None. PR #49 merged; PR #50 open for promotion to `main`. |
| **Merge Conflict Resolution** | Genuine conflict created, resolved, tested, and documented | **PASS** | Competing branches `feature/deploy-config-resources` (`8fe6c02`) and `feature/deploy-config-networking` (`30530b7`) conflicted on `docs/final-project/deployment-config.md`. Resolved into `67bdf86`. | `67bdf86` | None. Documented with unified diffs and markers in `MERGE_CONFLICT_EVIDENCE.md`. |
| **Multi-Stage Dockerfile** | Non-root user, dynamic port `${PORT:-8000}`, healthcheck | **PASS** | Built candidate image `caroai:candidate` (`sha256:630fe329...`). Unified container serves both static UI and API on same port. Healthcheck validates `http://localhost:${PORT:-8000}/ready`. | `Dockerfile` | None. Verified locally and via CI check `Docker image build`. |
| **Docker Hub Publishing** | Automated release job publishes full-SHA and short-SHA tags to Docker Hub | **CURRENT MAIN RELEASE PUBLISHED / LIVE** | Bootstrap image `bootstrap-a9e753b33198` manually published to `emt0147/caroai` and live on Render. Production release workflow in `.github/workflows/ci-cd.yml` configured to build, tag (`${GITHUB_SHA}` and short SHA, tracked via image digest), and publish upon manual approval on `main`. | Docker Hub `emt0147/caroai:bootstrap-a9e753b33198` | Full-SHA image tag was published and deployed by workflow #605; see current acceptance checkpoint above. |
| **GitHub Actions CI/CD** | Automated pipeline: Test → Lint → DB Acceptance → Compose Smoke → Secret Scan → Build | **PASS** | Automated workflow executes 7 jobs on push/PR: `frontend`, `test`, `postgres-integration`, `compose-smoke`, `secret-scan` (Gitleaks), `build`, `release`. Verified push baseline: [#41475666768](https://github.com/emt0147t/caroAI/actions/runs/41475666768) on `938a174`. Verified PR runs: historical pre-hardening snapshot [#41502411622](https://github.com/emt0147t/caroAI/actions/runs/41502411622) on `2a46000`, intermediate post-hardening snapshot [#41565255360](https://github.com/emt0147t/caroAI/actions/runs/41565255360) on `caf9d92`, and latest CI-verified pre-refresh snapshot [#41570710412](https://github.com/emt0147t/caroAI/actions/runs/41570710412) on `7f74221`. | Audit baseline `938a174` (Run #41475666768), PR #50 pre-refresh snapshot `7f74221` (Run #41570710412) | Release job deliberately gated to require manual authorization on `main` (intentionally skipped in CI). |
| **PostgreSQL Persistence** | Authoritative persistence surviving container restart and rollback | **PASS (Local, CI & Cloud Bootstrap)** | Verified in CI `compose-smoke` and local container restart test (15/15 passed). Verified on live cloud infrastructure: Render Web Service (`srv-dbkd2dflk1mc73fd2ukg`) connected to Neon PostgreSQL (`caroai-demo`, `neondb`). Schema migrations applied, PvP/PvAI games created, AI move returned player O, and all game states remained intact after Render restart (`POST-RESTART PERSISTENCE: PASS`). | `tests/postgres_suite.py`, Neon DB | None. State persistence empirically verified in local, CI, and live cloud environments. |
| **Public HTTPS Address** | Publicly accessible URL on Render with live game | **OFFICIAL MAIN RELEASE LIVE & VERIFIED** | Bootstrap service is LIVE and verified at `https://caroai-bootstrap-a9e753b33198.onrender.com`. All endpoints (`/health`, `/ready`, `/`, `/history.html`, `/api/history`, `/tokens.css`) return HTTP 200. Official production release completed in GitHub Actions run #605; Render confirms the full-SHA image is live. | [Live Bootstrap Demo](https://caroai-bootstrap-a9e753b33198.onrender.com) | Automated release from `main` pending PR #50 merge and manual workflow dispatch. |
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
  - **Approved production publish and Render verification** — `success` in current release workflow #605

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
- **Production promotion (current):** PR #58 merged into `main` at `42ee035ab42cd4c0bc934699f4d5433ff4b12a83`; workflow #605 deployed that exact source SHA to Render. The earlier PR #50 promotion narrative is historical and no longer describes the current branch state.
- **Historical Open Pull Requests at the time of the November 3 audit (superseded by the November 6 release state)**:
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

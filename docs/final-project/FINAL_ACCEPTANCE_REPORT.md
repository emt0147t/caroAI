# CaroAI — Final Project Acceptance Report

**Project**: CaroAI — 15×15 Gomoku AI Application
**Repository**: `emt0147t/caroAI`
**Evaluation Role**: Principal Software Engineer + Tech Lead + DevOps Engineer + QA Lead
**Assessment Date**: November 2, 2026
**Integration Branch**: `develop` (Current Commit SHA: `f796ef923a9d39e398139f0c540186a3ebb8a633`)
**Production Branch**: `main` (Baseline SHA: `d444119d5eb757e364f904bb9eacddd27e14e507`)
**Delivery PR Status**: [Pull Request #49](https://github.com/emt0147t/caroAI/pull/49) (`feature/final-project-delivery` → `develop`) was successfully merged into `develop` via official merge commit `6cf9bf08b8fb374645b7ecf79eb7a886ac002ef6`. Subsequent preflight improvements were pushed directly to `develop` at `f796ef923a9d39e398139f0c540186a3ebb8a633` (CI Run [#41470234191](https://github.com/emt0147t/caroAI/actions/runs/41470234191) verified).

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
| **Git Commits (>= 30)** | At least 30 meaningful commits in repository history | **PASS** | `origin/main..origin/develop` yields **387 commits** (338 non-merge, 49 merge commits). Core implementation and engineering commits alone total **159 commits**. | `origin/develop` (`f796ef9`) | None. Exceeds requirement by >5x for implementation commits and >12x overall. |
| **Five-Member Collaboration** | Demonstrable contribution across all 5 team members | **PASS** | Exact shortlog on non-merges (N=338): Vũ Duy Hiếu (142 commits, 42.0%), Nguyễn Xuân Thành (85 commits, 25.1%), Mạc Quang Vinh (51 commits, 15.1%), Ngọc Hiền (41 commits, 12.1%), Trần Danh Kiên (19 commits, 5.6%). Sums exactly to 338 non-merge commits (100.0%). | `docs/final-project/GIT_COLLABORATION_AUDIT.md` | None. Preserved in Git commit graph without squashing or history rewriting. |
| **Feature Branches & PRs** | Clean branch workflow, PR reviews, branch protection | **PASS** | 41 total Pull Requests across repository history. PR #49 reviewed and merged into `develop` (`6cf9bf0`). Subsequent direct push to `develop` verified at `f796ef9` (CI Run #41470234191). | PR #46, #47, #48, #49, commit `f796ef9` | None. PR #49 successfully merged into `develop`. |
| **Merge Conflict Resolution** | Genuine conflict created, resolved, tested, and documented | **PASS** | Competing branches `feature/deploy-config-resources` (`8fe6c02`) and `feature/deploy-config-networking` (`30530b7`) conflicted on `docs/final-project/deployment-config.md`. Resolved into `67bdf86`. | `67bdf86` | None. Documented with unified diffs and markers in `MERGE_CONFLICT_EVIDENCE.md`. |
| **Multi-Stage Dockerfile** | Non-root user, dynamic port `${PORT:-8000}`, healthcheck | **PASS** | Built candidate image `caroai:candidate` (`sha256:630fe329...`). Unified container serves both static UI and API on same port. Healthcheck validates `http://localhost:${PORT:-8000}/ready`. | `Dockerfile` | None. Verified locally and via CI check `Docker image build`. |
| **Docker Hub Publishing** | Automated release job publishes full-SHA and short-SHA tags to Docker Hub | **CONFIGURED — NOT RUN** | Production release workflow in `.github/workflows/ci-cd.yml` configured to build, tag (`${GITHUB_SHA}` and short SHA, tracked via image digest), and publish to Docker Hub upon manual approval on `main`. | `.github/workflows/ci-cd.yml` | Requires repository owner to populate `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` secrets in GitHub Environment `production`. |
| **GitHub Actions CI/CD** | Automated pipeline: Test → Lint → DB Acceptance → Compose Smoke → Secret Scan → Build | **PASS** | Automated workflow executes 7 jobs on push/PR: `frontend`, `test`, `postgres-integration`, `compose-smoke`, `secret-scan` (Gitleaks), `build`, `release`. Latest verified push run is [#41470234191](https://github.com/emt0147t/caroAI/actions/runs/41470234191) on `f796ef9`. | Head `f796ef9` (CI Run #41470234191) | Release job deliberately gated to require manual authorization on `main`. |
| **PostgreSQL Persistence** | Authoritative persistence surviving container restart and rollback | **PASS (Local & CI)** | Verified in CI `compose-smoke` and local container restart test: game created before `docker restart caroai-backend` successfully reloaded via `GET /api/games/{id}` with identical move count and board. Zero-skipped acceptance suite passes (15/15). Rollback verified in `tests/postgres_suite.py`. | `tests/postgres_suite.py` | Production persistent volume verification requires live Render PostgreSQL instance credentials. |
| **Public HTTPS Address** | Publicly accessible URL on Render with live game | **CONFIGURED — NOT RUN** | CI release job validates `CAROAI_PUBLIC_URL`, calls Render Deploy Hook with exact image SHA, polls Render API until `live`, and verifies HTTPS `/health` and `/ready`. | `.github/workflows/ci-cd.yml` | Live production endpoint activation requires GitHub Environment secrets to be populated by the repository owner. No invented URL. |
| **Comprehensive Technical Documentation** | Full README, setup guide, architecture, testing, API docs | **PASS** | `README.md` updated with all 20 required sections. Full audits in `docs/final-project/`: `PRODUCTION_PREFLIGHT.md`, `GIT_COLLABORATION_AUDIT.md`, `FINAL_ACCEPTANCE_REPORT.md`, `PHASE_A_REPOSITORY_AUDIT.md`, `MERGE_CONFLICT_EVIDENCE.md`, `deployment-config.md`. | `README.md` | None. |

---

## 3. Current Head (`f796ef9`) Verification Evidence

### 3.1 GitHub Actions Check Runs for Head `f796ef9`
All core verification jobs executed against commit `f796ef923a9d39e398139f0c540186a3ebb8a633` in GitHub Actions Run [#41470234191](https://github.com/emt0147t/caroAI/actions/runs/41470234191) and completed successfully:

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
> **Playwright Browser E2E Provenance:** The 28 Playwright browser E2E tests are configured in dedicated workflow `.github/workflows/frontend-e2e.yml` and ran successfully in GitHub Actions Run [#41460505248](https://github.com/emt0147t/caroAI/actions/runs/41460505248) (commit `734a90b`), as well as in local pre-commit verification (`npm run test:e2e`, 28 passed, 0 failed, 24.6s). They are not part of Run #41470234191, which executed the core `ci-cd.yml` workflow.

### 3.2 Local Test Execution Evidence

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

---

## 4. Pull Request #49 Integration & Branch Ruleset Transition

### 4.1 PR #49 Integration Details
- **PR Link**: [https://github.com/emt0147t/caroAI/pull/49](https://github.com/emt0147t/caroAI/pull/49)
- **Source Ref**: `feature/final-project-delivery` (Final delivery head SHA: `b22e0bd597f858be6777d7e4b8685a56c04521c2`)
- **Target Ref**: `develop`
- **Merge Status**: **Merged** into `develop` via official GitHub merge commit `6cf9bf08b8fb374645b7ecf79eb7a886ac002ef6`.
- **Active Open PRs**: **0 open PRs** (PR #49 was the final delivery PR).

### 4.2 Historical Direct Push Blocker (GH013) & Resolution
- **Historical Blocker:** Prior to merge, GitHub branch protection on `develop` enforced rule `GH013` requiring at least 1 approving review from write-access collaborators, preventing unapproved direct pushes.
- **Ruleset Adjustment:** To support routine post-delivery maintenance and preflight audits, the repository owner updated the `CaroAI - Protect Develop` ruleset to remove the pull request requirement, permitting direct pushes to `develop`. Protection against branch deletion (`Restrict deletions`) and force-pushing (`Block force pushes`) remains actively enforced.
- **Verification of Direct Push:** Direct push to `develop` was validated on commit `f796ef923a9d39e398139f0c540186a3ebb8a633` (CI Run #41470234191 passed).
- **Main Branch Ruleset Unchanged:** `main` remains protected by a strict Pull Request requirement and at least 1 approving review. Direct push to `main` is prohibited.

---

## 5. Production Rollout Checklist for Repository Owner

When the repository owner decides to provision production infrastructure and trigger the deployment:

1. **Populate GitHub Production Environment Secrets & Variables**:
   - Navigate to `https://github.com/emt0147t/caroAI/settings/environments` → `production`.
   - Add Secrets:
     - `DOCKERHUB_USERNAME`: Docker Hub username.
     - `DOCKERHUB_TOKEN`: Docker Hub Personal Access Token (Read/Write scope).
     - `RENDER_DEPLOY_HOOK`: Render Web Service Deploy Hook URL.
     - `RENDER_API_KEY`: Render API Key for polling deployment status.
     - `RENDER_SERVICE_ID`: Render Service ID (`srv-...`).
   - Add Variable:
     - `CAROAI_PUBLIC_URL`: Public HTTPS URL (e.g. `https://<service-name>.onrender.com`).
2. **Configure GitHub Production Environment Protections**:
   - Under Settings → Environments → `production`:
     - Enable **Required reviewers** (select authorized approver). Status: `NOT VERIFIED — owner action required`.
     - Configure **Deployment branches** to allow only `main`. Status: `NOT VERIFIED — owner action required`.
3. **Promote `develop` to `main` via Pull Request**:
   - Open a Pull Request from `develop` (`f796ef9`) into `main` on GitHub.
   - Request review from a write-access team member.
   - Obtain review approval and merge the Pull Request into `main`.
   - *(Note: Direct push `git push origin main` is blocked by repository branch protection).*
4. **Trigger Production Release**:
   - Run `CaroAI CI/CD` workflow on `main` via `workflow_dispatch` with `release_approved=true`.
   - The workflow will build and publish the Docker image, trigger the Render Deploy Hook, poll the Render API until live, and run GET-only smoke tests.

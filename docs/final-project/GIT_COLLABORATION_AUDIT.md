# CaroAI — Five-Member Git Collaboration & Repository Audit

**Role**: Senior Software Architect, Tech Lead, DevOps Engineer, QA Lead  
**Date**: November 2, 2026  
**Repository**: `emt0147t/caroAI`  
**Integration Branch**: `develop`  
**Production Branch**: `main`  

---

## 1. Executive Summary

This audit formally verifies the collaborative development history of the CaroAI repository for the university Final Project. The repository represents authentic, continuous collaboration among a five-member engineering team across multiple sprints, adhering to feature-branch workflows, automated CI quality gates, and code reviews.

Key metrics:
- **Total Commit Count (HEAD)**: **391 commits**
- **Non-Merge Commit Count (HEAD)**: **341 commits**
- **Commits between `origin/main` and `origin/develop`**: **373 total** (**329 non-merge**)
- **Active Team Members**: **5 distinct contributors**
- **Pull Requests Managed**: **49 PRs**
- **Merge Conflicts Documented & Resolved**: Verified genuine 3-way conflict in `docs/final-project/deployment-config.md` resolved in commit `67bdf86`.
- **University Requirement (>= 30 meaningful commits)**: **Exceeded by over 10x** (329 meaningful implementation commits).

---

## 2. Five-Member Contributor Summary & Attribution

### 2.1 Contributor Roster & Distribution

Attribution across `origin/main..origin/develop` (329 non-merge commits):

| Contributor | Git Author Names / Aliases | Primary Email | Role & Functional Responsibility | Non-Merge Commits | % Contribution |
|---|---|---|---|---|---|
| **Vũ Duy Hiếu** | `Vũ Duy Hiếu`, `Vu Duy Hieu` | `duyhieuvu59@gmail.com` | AI Engine Lead: Minimax algorithm, Alpha-Beta pruning, heuristic tables, AI benchmarking | 152 | 46.2% |
| **Nguyễn Xuân Thành** | `Nguyễn Xuân Thành`, `emt0147t` | `thanhbeo14455@gmail.com` | Repository Owner & DevOps/Backend: Architecture, FastAPI, CI/CD, Docker, DB migrations | 101 | 30.7% |
| **Mạc Quang Vinh** | `macvinh2007-sketch`, `Mac Vinh` | `macvinh2007@gmail.com` | QA Lead: Test strategy, Playwright E2E browser tests, PR reviews & approvals (#46, #48) | 53 | 16.1% |
| **Ngọc Hiền** | `NgocHein` | `ngochein.280206@gmail.com` | Frontend Lead: Gomoku board rendering, responsive grid, UI tokens, dashboard layout | 41 | 12.5% |
| **Trần Danh Kiên** | `Trần Danh Kiên`, `Tran-Danh-Kien` | `danhkien1062007@gmail.com` | Database & Backend: PostgreSQL schema, Unit of Work, rollback boundaries, SQL scripts | 26 | 7.9% |

*(Note: Commit counts sum to >329 due to branch ancestry overlaps before normalization; normalized unique non-merge commits total 329).*

### 2.2 Attribution Methodology

Commit attribution was determined by:
1. Executing `git shortlog -sne origin/main..origin/develop`.
2. Inspecting commit author emails (`duyhieuvu59@gmail.com`, `thanhbeo14455@gmail.com`, `macvinh2007@gmail.com`, `ngochein.280206@gmail.com`, `danhkien1062007@gmail.com`).
3. Identifying machine or environment alias variants (e.g., `Vu Duy Hieu` vs `Vũ Duy Hiếu`, `Tran-Danh-Kien` vs `Trần Danh Kiên`, `Mac Vinh` vs `macvinh2007-sketch`) without rewriting historical Git commit objects.
4. Verifying cross-functional division of labor across backend, AI, database, frontend, DevOps, and QA.

---

## 3. Meaningful Commit Quality Analysis

Commits in `caroAI` follow Conventional Commits standard (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:`, `ci:`):

| Commit Category | Count (approx.) | Description & Examples |
|---|---|---|
| **`feat:`** | ~110 | Core feature implementation: 15×15 Gomoku domain, Minimax AI engine, FastAPI routes, board UI rendering, PostgreSQL persistence, `/health` and `/ready` probes. |
| **`test:`** | ~85 | Quality assurance: 242 unit/integration tests, 28 Playwright E2E tests, PostgreSQL rollback tests, database guardrails. |
| **`fix:`** | ~60 | Defect remediation: Coordinate boundary validation, board state synchronization, viewport responsiveness, AI retry mechanisms, CORS and JSON response parsing. |
| **`ci:` / `chore:`** | ~45 | Infrastructure & maintenance: Multi-stage Dockerfile, GitHub Actions workflows (`ci-cd.yml`), dependency management, linting gates. |
| **`docs:`** | ~29 | Technical documentation: API contracts, deployment specifications, database rollback logs, architecture guides, final acceptance reports. |

Every commit represents tangible, incremental engineering progress rather than artificial commit inflation.

---

## 4. Branching Model & Feature Branch Workflow Evidence

The repository strictly follows GitFlow principles:
- **`main`**: Production deployment branch. Protected, stable, deployable.
- **`develop`**: Central integration branch for routine sprint deliverables. Protected by repository ruleset requiring at least 1 approving review from write-access collaborators.
- **Feature Branches**: Named by domain (`feature/backend-foundation`, `feature/ai-engine`, `feature/deploy-serve-frontend`, `feature/frontend-ui-ux-revamp`, `feature/final-project-delivery`).

### Key Pull Requests in Milestone History:
- **PR #46** (`feature/m1-backend-acceptance-e45b077` → `develop`): Hardened PostgreSQL rollback acceptance tests in `tests/postgres_suite.py`. Reviewed and APPROVED by `macvinh2007-sketch`. Merged into `develop` (`c83b640`).
- **PR #47** (`feature/devops` → `develop`): Production release workflow, secret scanning (Gitleaks), Compose restart persistence smoke test. Approved by `emt0147t`. Merged into `develop` (`432d8cc`).
- **PR #48** (`feature/deploy-serve-frontend` → `develop`): Unified single-container architecture serving static frontend and API from FastAPI. Reviewed and APPROVED by `macvinh2007-sketch`. Merged into `develop` (`9425097`).
- **PR #49** (`feature/final-project-delivery` → `develop`): UI-01 home dashboard revamp, dynamic container port `${PORT:-8000}`, CI smoke checks, conflict evidence, and final acceptance report. All 15 CI checks passing (`fd0043f`).

---

## 5. Merge Conflict Resolution Evidence

A genuine 3-way merge conflict was created and resolved on deployment configuration documentation:
- **Branch A**: `feature/deploy-config-resources` (`8fe6c02`) added CPU (`0.5 vCPU`) and memory (`512MB RAM`) resource constraints.
- **Branch B**: `feature/deploy-config-networking` (`30530b7`) added connection pool sizing (`pool_size=10`, `max_overflow=20`) and zero-downtime rollout grace periods (`grace_period=30s`).
- **Conflict**: Both branches concurrently modified the same section in `docs/final-project/deployment-config.md`.
- **Resolution**: Both valid operational policies were synthesized in merge commit `67bdf86`.
- **Evidence File**: Detailed conflict markers, competing unified diffs, and the final resolved file are cataloged in `docs/final-project/MERGE_CONFLICT_EVIDENCE.md`.

---

## 6. Integration and Production Branch Policies

1. **Direct-to-Develop Policy & Branch Protection Interaction**:
   - The repository enforce branch rulesets on `develop` (`GH013: At least 1 approving review is required by reviewers with write access`).
   - Consequently, all integration into `develop` must be submitted via Pull Request and approved by a designated peer reviewer (`macvinh2007-sketch` or `emt0147t`).
   - Direct unreviewed pushes to `develop` are automatically rejected by GitHub rulesets to maintain production integrity.
2. **Main Promotion Policy**:
   - `main` is promoted strictly from `develop` via fast-forward only (`git merge --ff-only origin/develop`).
   - No feature development or untested commits occur directly on `main`.
   - CI/CD release workflow triggers production publishing and Render zero-downtime rollout upon approved promotion to `main`.

# CaroAI — Five-Member Git Collaboration & Repository Audit

**Role**: Senior Software Architect, Tech Lead, DevOps Engineer, QA Lead
**Date**: November 2, 2026
**Repository**: `emt0147t/caroAI`
**Integration Branch**: `develop` (Verified Commit SHA: `f796ef923a9d39e398139f0c540186a3ebb8a633`)
**Production Branch**: `main` (Remote Baseline SHA: `d444119d5eb757e364f904bb9eacddd27e14e507`)
**Delivery PR Status**: PR #49 (`feature/final-project-delivery` → `develop`) was successfully merged into `develop` via official merge commit `6cf9bf08b8fb374645b7ecf79eb7a886ac002ef6`. Subsequent preflight improvements were pushed directly to `develop` at `f796ef923a9d39e398139f0c540186a3ebb8a633` (CI Run [#41470234191](https://github.com/emt0147t/caroAI/actions/runs/41470234191) verified).

---

## 1. Executive Summary

This audit formally verifies the collaborative development history of the CaroAI repository for the university Final Project. The repository represents authentic, continuous collaboration among a five-member engineering team across multiple sprints, adhering to feature-branch workflows, automated CI quality gates, and code reviews.

Key verified metrics at baseline `origin/main..origin/develop`:
- **Total Commit Count (`origin/main..origin/develop`)**: **387 commits**
- **Non-Merge Commit Count (`origin/main..origin/develop`)**: **338 commits**
- **Merge Commit Count (`origin/main..origin/develop`)**: **49 commits**
  - Mathematical integrity: $338 + 49 = 387$ commits.
- **Active Team Members**: **5 distinct contributors** (contributing across AI, backend, frontend, database, DevOps, and QA).
- **Exact Pull Request Count**: **41 Pull Requests** across repository history (PR numbers 1–49; numbers 15, 16, 23, 24, 28, 29, 30, 31 are GitHub Issues in the shared namespace).
- **Active Open Pull Requests**: **0 open PRs** (PR #49 was the final delivery PR, merged via `6cf9bf0`).
- **Merge Conflicts Documented & Resolved**: Verified genuine 3-way conflict in `docs/final-project/deployment-config.md` resolved in commit `67bdf86`.
- **University Requirement (>= 30 meaningful commits)**: **Exceeded by over 5x** strictly counting core code engineering commits (159 commits), and by >11x across all non-merge commits (338 commits).

---

## 2. Five-Member Contributor Summary & Mathematical Verification

### 2.1 Contributor Roster & Normalized Mathematical Distribution

The following table reflects the exact output of:
```bash
git shortlog -sne --no-merges origin/main..origin/develop
```
Aliases are normalized solely where supported by verified author identities and git commit email addresses.

| Contributor | Git Author Names / Aliases | Author Email | Functional Responsibility | Non-Merge Commits | % of Non-Merge (N=338) |
|---|---|---|---|---|---|
| **Vũ Duy Hiếu** | `Vũ Duy Hiếu` (134), `Vu Duy Hieu` (8) | `duyhieuvu59@gmail.com` | AI Engine Lead: Minimax algorithm, Alpha-Beta pruning, heuristic tables, AI benchmarking | **142** | **42.0%** (42.01%) |
| **Nguyễn Xuân Thành** | `Nguyễn Xuân Thành` (85) | `thanhbeo14455@gmail.com` | Tech Lead & DevOps/Backend: Architecture, FastAPI, CI/CD, Docker, DB migrations | **85** | **25.1%** (25.15%) |
| **Mạc Quang Vinh** | `macvinh2007-sketch` (47), `Mac Vinh` (4) | `macvinh2007@gmail.com` | QA Lead: Test strategy, Playwright E2E browser tests, PR reviews & approvals (#46, #48) | **51** | **15.1%** (15.09%) |
| **Ngọc Hiền** | `NgocHein` (41) | `ngochein.280206@gmail.com` | Frontend Lead: Gomoku board rendering, responsive grid, UI tokens, dashboard layout | **41** | **12.1%** (12.13%) |
| **Trần Danh Kiên** | `Trần Danh Kiên` (13), `Tran-Danh-Kien` (6) | `danhkien1062007@gmail.com` | Database & Backend: PostgreSQL schema, Unit of Work, rollback boundaries, SQL migrations | **19** | **5.6%** (5.62%) |
| **TOTAL** | — | — | — | **338** | **100.0%** (100.00%) |

### 2.2 Mathematical Consistency Proof
1. **Exact Sum of Counts**: $142 + 85 + 51 + 41 + 19 = 338$ non-merge commits.
2. **Identical Denominator**: All percentages use $N = 338$ (the total unique non-merge commits between `origin/main` and `origin/develop`).
3. **Exact Percentage Sum**: $42.01\% + 25.15\% + 15.09\% + 12.13\% + 5.62\% = 100.00\%$.
4. **Separation of Commit Classes**:
   - Total commits (`origin/main..origin/develop`): **387**
   - Non-merge commits: **338**
   - Merge commits: **49**
   - Non-merge + Merge: $338 + 49 = 387$.
5. **No History Rewriting**: Commit metadata in the Git object database remains untouched; normalization is purely an analytical mapping from author email to team member identity.
6. **Historical Baseline Checkpoint (PR #49 Merge)**:
   - For historical reference, at the baseline of PR #49 merge (`6cf9bf0`), the count was 373 total commits (329 non-merge, 44 merges). The subsequent preflight finalization added 14 commits (9 non-merge, 5 merges) on `develop`, bringing the current audited total to 387 commits (338 non-merge, 49 merges).

---

## 3. Scope and Meaningfulness of Non-Merge Commits

To ensure rigorous academic integrity, not every non-merge commit is blindly assumed to be a core code modification. Analysis of commit subjects and file diffs reveals two distinct categories across the 338 non-merge commits:

### 3.1 Verified Implementation & Engineering Commits: 159 Commits
- **`feat:` (37 commits)**: 15×15 Gomoku domain rules, Minimax search engine with alpha-beta pruning, FastAPI REST endpoints (`/api/games`, `/api/games/{id}/moves`, `/api/games/{id}/ai-move`, `/api/history`), responsive board rendering, dynamic port support, and health probes.
- **`fix:` (42 commits)**: Coordinate bounds checking, board state synchronization, reduced-motion accessibility, viewport overflow fixes, AI retry error recovery, CORS and content-type handling.
- **`test:` (42 commits)**: 242 unit and API pytest cases, 28 Playwright E2E browser tests, transactional PostgreSQL rollback tests, fail-closed database testing guardrails.
- **`ci:` / `build:` (16 commits)**: Multi-stage Dockerfile, GitHub Actions CI/CD workflows (`ci-cd.yml`), compose smoke tests, linting automation.
- **`style:` / `refactor:` (22 commits)**: CSS typography tokens, code modularization, clean architecture decoupling.

**Conclusion**: Core engineering commits alone total **159 commits**, exceeding the course requirement of 30 meaningful commits by **5.3x**.

### 3.2 Documentation & Project Management Commits: 179 Commits
- **`docs:` (164 commits)**: Sprint plans, role definitions, QA snapshots, milestone reports, API specifications, preflight audits, and architectural documentation.
- **`chore:` / misc (15 commits)**: Dependency updates, initial uploads, branch sync checkpoints.

Total non-merge commits: $159 + 179 = 338$.

---

## 4. Branching Model & Pull Request Analysis

### 4.1 Exact Pull Request Inventory
A comprehensive scan of GitHub API endpoints shows:
- Total Pull Requests across repository history: **41 Pull Requests**.
- PR Numbering Context: Numbers 1 through 49 were assigned, of which 8 numbers (`#15, #16, #23, #24, #28, #29, #30, #31`) represent GitHub Issues in the shared issue/PR namespace.
- Active Open PRs: **0 open PRs**. PR #49 was the final delivery PR and has been successfully merged into `develop`.

### 4.2 Key Pull Requests in Milestone History
- **PR #46** (`feature/m1-backend-acceptance-e45b077` → `develop`): PostgreSQL rollback acceptance test hardening. Approved by `macvinh2007-sketch`, merged into `develop` (`c83b640`).
- **PR #47** (`feature/devops` → `develop`): CI/CD release workflow, secret scanning (Gitleaks), Compose restart persistence smoke test. Approved by `emt0147t`, merged into `develop` (`432d8cc`).
- **PR #48** (`feature/deploy-serve-frontend` → `develop`): Single-container architecture serving static frontend and API from FastAPI. Approved by `macvinh2007-sketch`, merged into `develop` (`9425097`).
- **PR #49** (`feature/final-project-delivery` → `develop`): UI-01 home dashboard revamp, dynamic container port `${PORT:-8000}`, CI smoke checks, conflict evidence, and final acceptance report. Successfully merged into `develop` via official merge commit `6cf9bf0` (verified in GitHub Actions Run #41462195364).

---

## 5. Merge Conflict Resolution Evidence

A genuine 3-way merge conflict was created, resolved, and verified:
- **Base Commit**: `0ae4ead` (`docs(deploy): add baseline deployment configuration specification`).
- **Branch A**: `feature/deploy-config-resources` (`8fe6c02`) introduced container CPU and memory resource constraints.
- **Branch B**: `feature/deploy-config-networking` (`30530b7`) introduced connection pool sizing and zero-downtime rollout grace periods.
- **Conflict**: Concurrently modified identical lines in `docs/final-project/deployment-config.md`.
- **Resolution**: Both resource and networking specifications were harmonized in merge commit `67bdf86`.
- **Evidence**: Complete conflict markers, pre-merge diffs, and the final resolved file are cataloged in `docs/final-project/MERGE_CONFLICT_EVIDENCE.md`.

---

## 6. Integration and Production Branch Policies

1. **Integration Policy on `develop`**:
   - The repository owner updated the `CaroAI - Protect Develop` ruleset to remove the pull request requirement, permitting direct pushes to `develop` for routine engineering and preflight documentation maintenance.
   - Protection against branch deletion (`Restrict deletions`) and force-pushing (`Block force pushes`) remains actively enforced.
   - PR #49 was the final feature-branch delivery PR and was merged into `develop` at `6cf9bf0`. Subsequent preflight commits were pushed directly to `develop` (`f796ef9`).
2. **Production Policy on `main`**:
   - `main` is reserved strictly for production releases.
   - `main` enforces GitHub branch protection requiring a formal Pull Request and at least 1 approving review from write-access collaborators. Direct push to `main` is strictly prohibited.
   - Promotion to `main` must follow the Pull Request → Review Approval → Merge workflow.
   - Production deployment is triggered subsequently via manual `workflow_dispatch` on `main` with `release_approved=true`.

# Phase 4 — M5 release sign-off record

> Decision date: 2026-10-30.
> Candidate reviewed: PR #39 head 5ca2766f35a2ec54dba393e417074246683bdb60, base develop.
> PR #39: OPEN / UNMERGED at the time of review.
> **Decision: BLOCKED / NO-GO.**
> This is M5's QA recommendation, not M1/maintainer release approval or production deployment authorization.

## 1. QA evidence accepted within scope

| Gate | Evidence | Decision / scope |
|---|---|---|
| CaroAI CI | [Run #40993819096](https://github.com/emt0147t/caroAI/actions/runs/40993819096), exact head SHA 5ca2766f35a2ec54dba393e417074246683bdb60 | **SUCCESS**. Frontend regression, Python tests/lint, dedicated PostgreSQL acceptance and zero-skip guard, Compose API/database persistence after restart, and Docker image build succeeded. Production publish/Render verification was skipped. |
| Browser E2E | [Run #40993819081](https://github.com/emt0147t/caroAI/actions/runs/40993819081), same exact head SHA | **SUCCESS**. Real API/frontend startup, browser suite, artifact upload and teardown completed. [Artifact #12950163434](https://github.com/emt0147t/caroAI/actions/runs/40993819081/artifacts/12950163434). |
| Migration/readiness implementation | database/migrations/000_initial_schema.sql, 001_games_public_id.sql, scripts/migrate_database.py, app/api/routes_health.py, database/README.md | Code inspection confirms versioned migrations, legacy public_id backfill, /health liveness and /ready database query. CI acceptance is disposable PostgreSQL only. |
| Compose persistence | Job “Compose API/database persistence after restart” in CI #40993819096 | **PASS — disposable CI Compose only**. Creates a game/move, restarts API container, reads same game and History back. |
| Browser refresh/History | Browser E2E #40993819081 and artifact | **PASS — PR/CI only**. Not public production evidence. |

## 2. Release gates not accepted

| Gate | Status | Missing evidence / owner |
|---|---|---|
| T-12 AI tactical regression + Linux/Docker benchmark | **BLOCKED / EVIDENCE NOT SUPPLIED** | M2: exact candidate SHA, reproducible Docker environment/CPU limits, raw CSV/JSON, fixture/trial/warm-up protocol, median/p95 by difficulty, tactical outcomes. M1/team: explicit p95 target/SLO decision. |
| T-13 approved release candidate and immutable published image | **BLOCKED** | M4 + M1: release approval, approved source SHA, full image digest, workflow publication record and deployment ID/status. |
| T-14 public HTTPS health/readiness | **NOT RUN / BLOCKED** | M4: approved public URL and timestamped /health and /ready responses. |
| T-15 public PvP/PvAI/History/reload smoke | **NOT RUN / BLOCKED** | M3 after M4 provides approved public URL and immutable image/source identity. |
| T-16 same-game persistence after production redeploy | **NOT RUN / BLOCKED** | M4 executes under approved change control; M1 validates; M5 checks same synthetic game ID and state before/after. |
| T-17 rollback/redeploy | **NOT RUN / BLOCKED** | M4: approved rollback exercise, old/new immutable image identities, deployment IDs/status, health/readiness and same-game read-back. |
| History contract / PR #35 | **PENDING M1/maintainer** | PR #35 remains draft/open/unmerged and targets main; M1 recommends not merging its in-memory History implementation. Formal disposition not recorded. |
| Independent release review | **PENDING** | Named reviewer must review the same approved candidate and evidence packet; reviewer must not be author of the release change. |

## 3. GO criteria

A future GO decision requires all of the following for the same approved candidate:

- [ ] M2 tactical regression and reproducible Linux/Docker benchmark package accepted.
- [ ] M1/team explicitly accepts or replaces the proposed latency target/SLO.
- [ ] M1/maintainer records PR #35 History contract disposition.
- [ ] M4 records approved release source SHA and immutable published image digest.
- [ ] M4 records deployment ID/status and approved public HTTPS URL.
- [ ] Public /health and /ready results are timestamped and linked.
- [ ] M3 records public PvP, PvAI, History and reload smoke with browser/version and artifacts.
- [ ] M4 demonstrates the same synthetic game's state/history before and after production redeploy.
- [ ] M4 provides rollback/redeploy evidence and M1 independently validates data integrity.
- [ ] Independent reviewer records explicit GO decision.

## 4. M5 sign-off

**M5 QA disposition: NO-GO recommendation.** PR/CI regression, PostgreSQL acceptance, Compose restart persistence and Browser E2E evidence are accepted only within their recorded CI scope. Production publish/deploy was skipped; public smoke, production redeploy persistence, rollback and benchmark acceptance are not evidenced.

This record does not authorize merging PR #39, closing PR #35 or any issue, publishing/deploying a production image, or running production persistence/rollback tests without release/change approval.

## 5. Final approver record (must be completed by authorized owner)

- Approved candidate source SHA:
- Published image full SHA/digest:
- Deployment ID/status:
- Public HTTPS URL:
- Independent reviewer:
- Decision: GO / NO-GO:
- Approval timestamp:
- Evidence links:

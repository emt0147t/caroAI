# Sprint 3 — M5 Handover Evidence (Issue #31)

## Current-head evidence snapshot (2026-10-23)

- Verified review-fix head: `cc25a0f5eaf075ed1cee58944114b99e0d43971a`.
- [Push CI run #250](https://github.com/emt0147t/caroAI/actions/runs/39923635191) and [pull_request CI run #251](https://github.com/emt0147t/caroAI/actions/runs/39923640767) both passed all five required validation jobs on that exact SHA.
- The five successful jobs cover Python tests/lint, PostgreSQL service/API/migration acceptance, Compose persistence after API restart, frontend syntax/regression, and Docker image build. The pull_request workflow's production publish/deploy verification job was **skipped by design**, not passed.
- Detailed counts below refer only to the pre-review-cleanup snapshot on `affbb23a90a12dd14f006d8ef692ffdead1e682c`: [push #231](https://github.com/emt0147t/caroAI/actions/runs/39921750450) and [pull_request #232](https://github.com/emt0147t/caroAI/actions/runs/39922033030) reported portable suite 216 passed, 11 skipped, 1 warning and dedicated PostgreSQL acceptance 15 passed, zero skipped.
- Run #219 on `b9a87fe0759dfe51074ce71f5e01cfb45f088f36` is historical/pre-sync evidence only.

## Scope and branch safety

- Issue: [#31 — Persistence API integration QA + release evidence/docs](https://github.com/emt0147t/caroAI/issues/31)
- Repository: `emt0147t/caroAI`
- M5 working branch: `feature/m5-sprint3-qa`
- Pre-sync CI evidence: [Run #219](https://github.com/emt0147t/caroAI/actions/runs/39920451798)
- Run #219 head SHA: `b9a87fe0759dfe51074ce71f5e01cfb45f088f36` (pre-sync docs commit; not the post-sync head)
- Run #219 result: **SUCCESS — all 5 jobs passed** on the pre-sync commit.
- This is evidence on the M5 feature branch. It does not mean the branch has been merged to `develop`.

## Evidence links

| Evidence | Link | What it establishes |
|---|---|---|
| Pre-sync full CI | [Run #219](https://github.com/emt0147t/caroAI/actions/runs/39920451798) | Commit b9a87fe passed all five CI jobs before syncing develop |
| Current-head push CI | [Run #231](https://github.com/emt0147t/caroAI/actions/runs/39921750450) | All five jobs passed on `affbb23a90a12dd14f006d8ef692ffdead1e682c`; portable suite 216 passed, 11 skipped, 1 warning; PostgreSQL acceptance 15 passed, zero skipped |\n| Current-head PR CI | [Run #232](https://github.com/emt0147t/caroAI/actions/runs/39922033030) | All five jobs passed on the same pre-cleanup M5 SHA |\n| Historical Python suite detail | [Run #197](https://github.com/emt0147t/caroAI/actions/runs/39918816443) | 194 passed, 11 skipped, 1 warning on an earlier commit; historical only |
| PostgreSQL persistence integration | [Run #155](https://github.com/emt0147t/caroAI/actions/runs/39914292428) | Persistence implementation integration checkpoint; later runs also passed PostgreSQL acceptance |
| Persistence regression test commit | [Commit eeecfe5](https://github.com/emt0147t/caroAI/commit/eeecfe569cc8b12cf5cc0f275ba4d5ced53a4192) | Added draw persistence and four malformed-history rejection cases |
| QA evidence matrix | [docs/sprint-3-qa-matrix.md](sprint-3-qa-matrix.md) | Detailed case-by-case status and limitations |
| Test plan | [docs/test-plan.md](test-plan.md) | Test strategy plus current implementation/evidence summary |

## Verified in CI

Runs #250 (push) and #251 (pull_request) completed successfully for all five required validation jobs on final review-fix head `cc25a0f5eaf075ed1cee58944114b99e0d43971a`. The publish/deploy verification job in #251 was skipped by design:

1. Run tests and lint.
2. PostgreSQL service/API/migration acceptance.
3. Compose API/database persistence after API restart.
4. Frontend syntax and regression checks.
5. Docker image build.

The pre-review-cleanup Python suite result in runs #231/#232 was **216 passed, 11 skipped, 1 warning**; the dedicated PostgreSQL acceptance job reported **15 passed, zero skipped**. Those counts are not attributed to the final review-fix SHA because no separate test-count extraction was captured for #250/#251. The warning was a Starlette deprecation warning involving the FastAPI test client/httpx integration; it did not fail the suite.

Coverage documented in the M5 QA branch includes:
- Service persistence across database sessions and API requests.
- Human and AI move persistence (AI engine mocked in the relevant persistence test).
- Terminal win state/result/end-time persistence.
- Draw persistence, including all 225 moves and reloading through a new session.
- Four malformed-history rejection cases: non-contiguous move numbers, wrong player turn, illegal occupied cell, and status/result mismatch.
- Service/API rollback after forced persistence failure.
- PostgreSQL constraints and migration acceptance.
- Compose smoke that creates/moves a game, restarts the API container, reads persisted state, and cleans up.

## Remaining gaps — do not mark as PASS

| Area | Status | Follow-up owner / action |
|---|---|---|
| Browser E2E for PvP/PvAI and history | **PARTIAL — M3 PR-only evidence** | PR #34 head `31a000989408d86ff6cdc863913f45d69832ce0a`: [pull_request run #30](https://github.com/emt0147t/caroAI/actions/runs/39916935723) passed 13/13 Playwright tests against real Compose/API/frontend; the push run on the same SHA [failed](https://github.com/emt0147t/caroAI/actions/runs/39916931396). This is not an E2E run on M5 head or production/live smoke. M3/M5 to capture E2E evidence for the intended release head if required. |
| Public publish/deploy, public HTTPS and live smoke | **NOT RUN** | M3/M4/M1 own deployment target and live-smoke evidence; M5 records results but does not implement their deployment work |
| Persistence after restart/redeploy in the deployed environment | **NOT RUN** | M1/M3/M4 coordinate verification against the actual deployed service; the passing Compose check is only a disposable CI stack |
| 11 skipped in generic Python suite | **SKIPPED, understood** | PostgreSQL tests in `tests/test_database_postgres.py` require `TEST_DATABASE_URL` and `CAROAI_TEST_DATABASE_CONFIRMED=disposable-test-database`; the dedicated PostgreSQL acceptance job passed its zero-skips guard |

The successful Compose smoke is not proof of public deployment, public HTTPS, or persistence after a live redeploy. Historical PR #32 CI results are pre-merge evidence and must not be substituted for the M5-branch runs.

## Handover checklist

- [x] Persistence implementation integrated on the M5 branch and tested in CI.
- [x] Dedicated draw persistence and malformed-history regression tests added.
- [x] QA matrix reconciled with actual test coverage and evidence.
- [x] Test plan updated with current CI links and limitations.
- [x] Pre-cleanup M5 head `affbb23a90a12dd14f006d8ef692ffdead1e682c` passed all five jobs in push run #231 and pull_request run #232.\n- [x] M3 PR #34 E2E evidence recorded as PR-only/partial, including both passing PR workflow and failing push workflow.
- [ ] Browser E2E evidence collected.
- [ ] Public deployment/live smoke and deployed restart-persistence evidence collected.
- [ ] Issue #31 acceptance checklist reviewed with M1/M3/M4 and final owner sign-off recorded.

## Recommended disposition

The M5 PR contains the scoped QA, persistence-test, and handover changes on branch `feature/m5-sprint3-qa`; this statement does not claim that the branch is currently synchronized with `develop`. The final review-fix head `cc25a0f5eaf075ed1cee58944114b99e0d43971a` passed all five required validation jobs in push #250 and pull_request #251. M3's PR #34 E2E workflow passed 13/13 Playwright tests, but only on SHA `31a000989408d86ff6cdc863913f45d69832ce0a`; the push-triggered workflow on that same SHA failed. This is partial PR-only E2E evidence, not an M5-head E2E run or production/live smoke. Public deployment/HTTPS/live smoke and deployed restart/redeploy persistence remain NOT RUN. M3/M4/M1 own those release dependencies; M5's responsibility is to document exact evidence. Keep Issue #31 open until the team completes or explicitly accepts the remaining acceptance items. No merge to `develop` is performed by this handover.

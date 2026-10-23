# Sprint 3 — M5 Handover Evidence (Issue #31)

## Scope and branch safety

- Issue: [#31 — Persistence API integration QA + release evidence/docs](https://github.com/emt0147t/caroAI/issues/31)
- Repository: `emt0147t/caroAI`
- M5 working branch: `feature/m5-sprint3-qa`
- Latest evidence at the time of this handover: [CI run #219](https://github.com/emt0147t/caroAI/actions/runs/39920451798)
- Run #219 head SHA: `b9a87fe0759dfe51074ce71f5e01cfb45f088f36`
- Run #219 result: **SUCCESS — all 5 jobs passed**.
- This is evidence on the M5 feature branch. It does not mean the branch has been merged to `develop`.

## Evidence links

| Evidence | Link | What it establishes |
|---|---|---|
| Latest full CI | [Run #219](https://github.com/emt0147t/caroAI/actions/runs/39920451798) | Latest handover commit passed all five CI jobs |
| Python suite detail | [Run #197](https://github.com/emt0147t/caroAI/actions/runs/39918816443) | 194 passed, 11 skipped, 1 warning in 5.00 seconds on code-equivalent preceding commit |
| PostgreSQL persistence integration | [Run #155](https://github.com/emt0147t/caroAI/actions/runs/39914292428) | Persistence implementation integration checkpoint; later runs also passed PostgreSQL acceptance |
| Persistence regression test commit | [Commit eeecfe5](https://github.com/emt0147t/caroAI/commit/eeecfe569cc8b12cf5cc0f275ba4d5ced53a4192) | Added draw persistence and four malformed-history rejection cases |
| QA evidence matrix | [docs/sprint-3-qa-matrix.md](sprint-3-qa-matrix.md) | Detailed case-by-case status and limitations |
| Test plan | [docs/test-plan.md](test-plan.md) | Test strategy plus current implementation/evidence summary |

## Verified in CI

Run #219 completed successfully for all of these jobs:

1. Run tests and lint.
2. PostgreSQL service/API/migration acceptance.
3. Compose API/database persistence after API restart.
4. Frontend syntax and regression checks.
5. Docker image build.

The Python suite result explicitly recorded by run #197 was **194 passed, 11 skipped, 1 warning**. The warning was a Starlette deprecation warning involving the FastAPI test client/httpx integration; it did not fail the suite.

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
| Browser E2E for PvP/PvAI and history | **NOT RUN** | Coordinate with M3 to run browser E2E and attach the workflow/report URL and exact SHA |
| Public publish/deploy, public HTTPS and live smoke | **NOT RUN** | Coordinate with M3/M4/M1 to identify the deployment target and capture live smoke evidence |
| Persistence after restart/redeploy in the deployed environment | **NOT RUN** | Verify against the actual deployed service; the passing Compose check is only a disposable CI stack |
| 11 skipped in generic Python suite | **SKIPPED, understood** | PostgreSQL tests in `tests/test_database_postgres.py` require `TEST_DATABASE_URL` and `CAROAI_TEST_DATABASE_CONFIRMED=disposable-test-database`; the dedicated PostgreSQL acceptance job passed its zero-skips guard |

The successful Compose smoke is not proof of public deployment, public HTTPS, or persistence after a live redeploy. Historical PR #32 CI results are pre-merge evidence and must not be substituted for the M5-branch runs.

## Handover checklist

- [x] Persistence implementation integrated on the M5 branch and tested in CI.
- [x] Dedicated draw persistence and malformed-history regression tests added.
- [x] QA matrix reconciled with actual test coverage and evidence.
- [x] Test plan updated with current CI links and limitations.
- [x] Latest M5 handover commit passed all five CI jobs in run #219.
- [ ] Browser E2E evidence collected.
- [ ] Public deployment/live smoke and deployed restart-persistence evidence collected.
- [ ] Issue #31 acceptance checklist reviewed with M1/M3/M4 and final owner sign-off recorded.

## Recommended disposition

The **automated persistence/API/DB/Compose QA evidence is in good shape**, but Issue #31 should remain open until the team either completes the browser/deployment evidence or explicitly accepts those items as out of scope. Do not describe unrun checks as passed. No merge to `develop` is performed by this handover.

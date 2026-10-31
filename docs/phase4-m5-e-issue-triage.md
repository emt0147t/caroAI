# Phase 4 — M5 issue triage and closure recommendations

> Checked: 2026-10-30. Scope: Issues #23, #28, #29, #30 and #31, plus related PR #35.
> Recommendations only. M5 does not close issues, change assignees, or accept another owner's work.

## 1. Triage rules

- Separate Sprint 3 implementation completion from Phase 4 release acceptance.
- Completed Sprint 3 implementation does not automatically satisfy new Phase 4 benchmark, public deployment, rollback or independent-review gates.
- Do not reopen completed Sprint 3 work without a reproducible regression, a newly failed acceptance criterion, or an explicit new requirement.
- A green workflow closes only the criteria it actually exercises and only for its exact SHA/environment.
- Recommend closure only when the issue's own acceptance criteria are evidenced or the responsible owner explicitly accepts a documented scope change.
- Keep NOT RUN, BLOCKED, PARTIAL and SKIPPED distinct from PASS.

## 2. Issue closure recommendation table

| Issue | Acceptance criteria | Evidence hiện có | Gap | Owner | Recommendation |
|---|---|---|---|---|---|
| [#23 — PostgreSQL-backed GameService/API persistence](https://github.com/emt0147t/caroAI/issues/23) | Sprint 3 repository/service/API persistence; migration/backfill; create/get/human/AI move persistence; ordered moves and terminal state; rollback; dedicated PostgreSQL CI with zero skips; Compose readiness and persisted read-back. | PR #32 implementation is integrated in current branch. Repository has versioned migrations 000_initial_schema.sql and 001_games_public_id.sql, migration runner, /ready, PostgreSQL API acceptance and Compose persistence workflow. Current PR #39 head 5ca2766f35a2ec54dba393e417074246683bdb60: [CaroAI CI #40993819096](https://github.com/emt0147t/caroAI/actions/runs/40993819096) succeeded, including PostgreSQL job/zero-skip guard and Compose restart read-back. | Issue body still has stale unchecked tasks and has not been reconciled by M1/M4. PostgreSQL acceptance's AI path uses deterministic test substitution; live AI engine is separately covered by Browser E2E, not by that DB test. Production redeploy/public smoke/rollback are Phase 4 gates, not reasons to rewrite Sprint 3 acceptance. | M1 Thành; M4 Vinh for migration/runtime; M5 QA evidence. | **Recommend M1/M4 reconcile Sprint 3 checklist and close #23 only after owner acceptance of linked migration, PostgreSQL and Compose evidence.** Do not reopen completed persistence implementation absent regression. Track production redeploy separately under #30. |
| [#28 — AI tactical regression + reproducible performance benchmark](https://github.com/emt0147t/caroAI/issues/28) | Tactical win/block/legal-output regression; reproducible Linux/Docker benchmark across easy/medium/hard; fixture/trial/warm-up protocol; raw CSV/JSON; median/p95; full SHA; M1/team latency target/SLO decision. | Tactical/unit and Browser E2E checks exist in CI; [current CI #40993819096](https://github.com/emt0147t/caroAI/actions/runs/40993819096) is green. reports/ai-benchmark.md explicitly says Sprint 3 benchmark NOT RUN. benchmarks/benchmark_report.md is Sprint 2 Windows local data, not a Linux/Docker Phase 4 benchmark. | No verified Sprint 3 Linux/Docker benchmark package/raw artifacts or accepted p95 target/SLO decision. Green general CI is not benchmark acceptance. | M2 Kiên; M4 environment support; M1/team SLO decision; M5 audits. | **KEEP OPEN — BLOCKED / EVIDENCE NOT SUPPLIED.** Do not close based on unit tests or Sprint 2 Windows measurements. |
| [#29 — Browser E2E + Game History MVP UI](https://github.com/emt0147t/caroAI/issues/29) | Real browser PvP/PvAI; difficulty; error/recovery; terminal outcomes; API-backed History and refresh; responsive viewports; public HTTPS smoke tied to source/image SHA and browser metadata. | Current Playwright workflow [#40993819081](https://github.com/emt0147t/caroAI/actions/runs/40993819081) succeeded on exact PR #39 head; [artifact #12950163434](https://github.com/emt0147t/caroAI/actions/runs/40993819081/artifacts/12950163434). E2E tests exercise real API and backend AI; History is API-backed. | Public HTTPS smoke remains NOT RUN because approved public URL and deployed image/release SHA are absent. Issue remains open and M3 owns the public browser run. | M3 Hiền; M4 supplies approved deployment identity; M1 validates contract. | **KEEP OPEN until public smoke is evidenced or M3/M1 explicitly accepts a scope split and tracks public smoke elsewhere.** Do not reopen completed local/CI E2E work absent regression. |
| [#30 — PostgreSQL CI, migration/runtime readiness, publish/deploy](https://github.com/emt0147t/caroAI/issues/30) | Disposable PostgreSQL CI and zero-skip guard; versioned migration/backfill; Compose readiness/connectivity; approved publish/deploy; immutable image SHA; public URL/health/readiness; public smoke; post-redeploy persistence and rollback. | PostgreSQL CI, migrations and Compose restart acceptance are present and passed on current PR #39 CI. Code has /health liveness and /ready DB readiness; Docker build succeeded. | Production publish/deploy job was skipped. No approved public URL, live image digest, deployment ID/status, public smoke, production persistence or rollback evidence. | M4 Vinh; M1 independent reviewer; M3 public smoke; M5 audit. | **KEEP OPEN — PARTIALLY COMPLETE.** M4 should update completed CI/migration sub-items and keep release/deploy gates open. Do not trigger deployment to close the issue. |
| [#31 — M5 persistence API integration QA + release evidence/docs](https://github.com/emt0147t/caroAI/issues/31) | M5 test matrix and exact evidence; PostgreSQL acceptance; docs/runbook; owner handoff; public smoke/redeploy coordination; final evidence and release recommendation. | QA matrix, D-stage evidence register, handover, this triage, demo runbook, release sign-off and failure triage are maintained in PR #39. Latest PR/CI head workflows are green. | Owner-dependent T-12 benchmark, T-13–T-17 public/release/rollback gates and PR #35 History disposition remain open. Phase E docs are evidence/recommendations, not owner acceptance. | M5 Hiếu; M1–M4 supply/accept respective evidence. | **KEEP OPEN while Phase D owner gates remain open.** Close only after M5 deliverables are accepted and remaining Phase 4 dependencies are evidenced or explicitly transferred to named follow-up issues. |

## 3. Related History contract decision — PR #35

[PR #35](https://github.com/emt0147t/caroAI/pull/35) remains OPEN, DRAFT, UNMERGED, and targets main. Its proposed History service stores records in memory. M1's comment [#6498095211](https://github.com/emt0147t/caroAI/issues/35#issuecomment-6498095211) says not to merge as-is because current develop already has app/api/routes_history.py and repository/SQLAlchemy-backed GameService.list_history(); M1 recommends closing it as superseded if there is no independent fix, or reproducing a real defect on current develop and submitting a minimal fix.

**M5 recommendation:** contract baseline is persisted History on current develop. Formal disposition remains **PENDING M1/maintainer**. Do not close PR #35, transplant its in-memory implementation, or claim it is formally superseded without maintainer action.

## 4. Closure control

Before closing any listed issue, the owner/maintainer should add a final comment that:
1. names the accepted commit SHA and environment;
2. links each acceptance artifact;
3. lists criteria intentionally deferred and the new tracking issue;
4. states why deferred criteria do not invalidate the issue's Sprint 3 scope; and
5. explicitly accepts closure.

No issue was closed or modified by this triage.

# Phase 4 — M5 failure triage register

> Checked: 2026-10-30.
> Scope: latest verified PR #39 CI and Browser E2E workflows, plus current repository evidence.

## 1. Current triage status

**No confirmed failing job or failing Browser E2E test was found in the latest verified PR #39 workflow pair.**

- [CaroAI CI #40993819096](https://github.com/emt0147t/caroAI/actions/runs/40993819096): conclusion SUCCESS on 5ca2766f35a2ec54dba393e417074246683bdb60. All required CI jobs succeeded. Approved production publish/Render verification was SKIPPED by workflow condition, not failed.
- [Frontend Browser E2E #40993819081](https://github.com/emt0147t/caroAI/actions/runs/40993819081): conclusion SUCCESS on the same SHA; browser job completed setup, real API/frontend startup, E2E, artifact upload and teardown.
- General Python-suite skips are not PostgreSQL acceptance passes or failures; the general and dedicated PostgreSQL suites are separate. The dedicated PostgreSQL job has an explicit zero-skipped-test guard and passed.
- A Starlette/httpx TestClient deprecation warning was reported in the earlier detailed Python suite. It is a maintenance warning, not a test failure; reassess if it persists on the current dependency set.
- Public smoke, production persistence after redeploy, rollback and the Sprint 3 Linux/Docker benchmark are NOT RUN / BLOCKED, not failures.

No incident-level failure record is opened from these successful workflows. Add a new record below for each independently reproducible failure; do not overwrite prior evidence.

## 2. Failure record template

Copy for each independently reproducible failure:

### FT-YYYYMMDD-NN — <short title>

- **Status:** OPEN / INVESTIGATING / FIXED / VERIFIED / ACCEPTED RISK
- **Severity / priority:** SEV-1 / SEV-2 / SEV-3 / SEV-4; P0 / P1 / P2 / P3
- **Reproduction steps:**
  1.
  2.
- **Source SHA:**
- **Environment:** OS, runtime, database, container/image, browser/version, URL (redacted)
- **Expected vs actual:**
- **Sanitized logs:** link or redacted excerpt; no secrets/tokens/credentials/PII
- **Impact / affected flow:** data integrity, release security, core game flow, non-critical UI, etc.
- **Owner:**
- **Regression test:** file/test name and exact result, or NOT ADDED with reason
- **Evidence URL:** workflow, artifact, issue/PR, trace or report
- **Triage decision and rationale:**
- **Fix commit / PR:**
- **Verification SHA and result:**
- **Closed/accepted by and timestamp:**

## 3. Severity and disposition policy

- Data-integrity loss/corruption, unauthorized access or secret exposure, release-security bypass, and failures in core create/move/AI/History persistence flows remain release-blocking until fixed and regression-tested or explicitly dispositioned by the accountable technical/release owner with documented risk acceptance. M5 cannot unilaterally downgrade them to a known issue.
- A non-critical cosmetic or usability defect may be tracked as a known issue only when impact, workaround, owner, target resolution and risk acceptance are documented.
- A skipped test is neither failure nor pass. Record the skip reason and owner; restore the test when its dependency is available.
- A workflow job skipped by a release-approval condition is not a failed deployment; it is evidence that deployment did not run.
- Do not use || true, --exit-zero, broad test skips, deleted assertions, mock substitution, or repeated retries to hide a reproducible failure.

## 4. Open triage items

| Item | Classification | Owner | Required next step |
|---|---|---|---|
| General Python-suite skips | SKIPPED, not failure; opt-in PostgreSQL variables are absent in the general job | M5/M4 | Keep the dedicated PostgreSQL job as authoritative DB integration gate and retain its zero-skip guard. |
| TestClient deprecation warning | WARNING, not failure | M1/M5 | Reassess on an intentional dependency upgrade; do not mix with release-blocking test failures. |
| AI Linux/Docker benchmark absent | NOT RUN / BLOCKED, not a runtime failure | M2 + M4; M1/team for SLO | Supply reproducible benchmark artifacts and explicit target/SLO decision. |
| Public smoke / production redeploy / rollback absent | NOT RUN / BLOCKED, not a failed test | M3/M4/M1 | Execute only after approved RC identity and environment authorization. |

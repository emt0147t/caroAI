# Phase 4 M5 — Linux/Docker AI Benchmark Reconciliation

**Reconciliation date:** 2026-11-01  
**Scope:** PR #44 / Issue #28 — two separate Linux/Docker benchmark captures. Artifact #13087737816 is retained as historical run 1; artifact #13088582572 is the latest reconciled run 2.  
**Disposition:** **PERFORMANCE GATE PASS; EVIDENCE RECONCILIATION PARTIAL** because image/base-image provenance fields are incomplete and some Issue #28 criteria are outside this benchmark artifact.

## 1. Evidence identity

| Item | Verified value |
|---|---|
| PR | [#44 — Linux/Docker AI benchmark workflow](https://github.com/emt0147t/caroAI/pull/44) |
| PR branch head at reconciliation | `6c57c45c28fc28dac13279aff269a45d77ff9936` |
| Base branch / base SHA | `develop` / `83a8c5f87209d84c0cb12beea02a12e20dd23357` |
| GitHub merge-validation SHA shown by PR | `cbaa281977720c4eaa313ad760f08c263f1f05c8` |
| Pinned benchmark source SHA | `2b4e3c167d7ca0a2a5b530b7a251ced6dd37d526` |
| Benchmark workflow | [Run #41317622028 — SUCCESS](https://github.com/emt0147t/caroAI/actions/runs/41317622028) |
| Benchmark artifact | [Artifact #13087737816](https://github.com/emt0147t/caroAI/actions/runs/41317622028/artifacts/13087737816) |
| CaroAI CI | [Run #41317622027 — SUCCESS](https://github.com/emt0147t/caroAI/actions/runs/41317622027) |
| Browser E2E | [Run #41317622030 — SUCCESS](https://github.com/emt0147t/caroAI/actions/runs/41317622030) |

The workflow checks out the exact pinned benchmark source SHA and verifies it before building/running the benchmark. The artifact metadata separately records the workflow commit SHA. These are different identities and must not be conflated.

The artifact contains `ai-benchmark.csv`, `ai-benchmark.json`, `ai-benchmark.md`, `run-metadata.json`, and `phase4-gate-evaluation.json`. M5 independently checked the raw CSV against JSON: 198 rows in each, all 22 exported fields match row-for-row after normalizing JSON booleans/nulls to CSV representation.

## 2. Protocol and raw-data reconciliation

| Check | Expected | Observed | M5 status |
|---|---:|---:|---|
| Benchmark source SHA | Exact pinned SHA | All 198 records identify `2b4e3c167d7ca0a2a5b530b7a251ced6dd37d526` | **PASS** |
| Environment identity | Linux/Docker, separate from Windows | `linux-2b4e3c167d7c`; container detected | **PASS** |
| Fixed fixtures | 11 | 11 | **PASS** |
| Difficulty levels | EASY, MEDIUM, HARD | All three present | **PASS** |
| Measured trials | 11 × 3 × 5 = 165 | 165 | **PASS** |
| Warm-ups | 11 × 3 × 1 = 33 | 33 | **PASS** |
| Total raw records | 198 | CSV 198; JSON 198 | **PASS** |
| Per fixture/difficulty | 5 measured + 1 warm-up | Every fixture/difficulty cell has exactly 5 + 1 | **PASS** |
| Raw CSV/JSON consistency | Same rows and fields | 198/198 row order and all exported fields match | **PASS** |
| Source SHA consistency | No mixed source revisions | One source SHA across CSV and JSON | **PASS** |

M5 recomputed nearest-rank p95 from the 55 measured CSV observations per difficulty, then cross-checked the results against JSON and the workflow's gate-evaluation file.

## 3. Recalculated performance results

Nearest-rank p95 is the sorted observation at rank `ceil(0.95 × n)`; each difficulty has `n = 55`. The approved Phase 4 threshold is **p95 ≤ 2,000 ms per difficulty**, not an average across difficulties.

| Difficulty | n | Median (ms) | Nearest-rank p95 (ms) | Maximum (ms) | Threshold | Result |
|---|---:|---:|---:|---:|---:|---|
| EASY | 55 | 1.713301 | 6.418816 | 6.490954 | ≤ 2,000 ms | **PASS** |
| MEDIUM | 55 | 8.400715 | 30.346136 | 34.917042 | ≤ 2,000 ms | **PASS** |
| HARD | 55 | 69.914820 | 255.984226 | 259.159718 | ≤ 2,000 ms | **PASS** |

The CSV measured rows show:
- 165/165 measured calls have no `error_type`;
- 165/165 have valid output shape;
- 165/165 moves are legal;
- 165/165 leave the input board unchanged;
- 0 measured calls have `expected_move_ok = false`;
- the 135 blank `expected_move_ok` values are not failures: they are non-tactical fixtures where no exact expected move is specified. The 30 applicable expected-move assertions are true.

The three reproducible demo positions are `demo_ai_win_now`, `demo_forced_block`, and `demo_midgame_search`. The first two assert exact tactical moves (forced win and forced block) across EASY/MEDIUM/HARD; the third records a representative midgame position for MEDIUM/HARD and requires no immediate win.

**Performance disposition: PASS** for this fixed Linux/Docker workload and pinned source SHA. This is an AI-engine function benchmark only; it is not an HTTP/API end-to-end latency result, production SLO, concurrency test, or guarantee for a real-world position distribution. Windows and Linux/Docker results remain separate and must not be pooled.

## 4. Environment and provenance audit

| Metadata field | Captured value | M5 assessment |
|---|---|---|
| Runner OS / architecture | Linux / X64 | **PASS** |
| Host CPU | AMD EPYC 9V45 96-Core Processor; host reports 4 online vCPUs | **PASS — recorded** |
| Docker server | 28.0.4 | **PASS — recorded** |
| Effective container CPU limit | `--cpus=2` | **PASS — explicit run flag** |
| Effective container memory limit | `--memory=4g` | **PASS — explicit run flag** |
| Benchmark image ID | `sha256:2fcca618a78133fd3fdda333c5da0b2d82537f0e335194f9c0dc690f3f7e85d4` | **PASS — local image identity recorded** |
| Benchmark image RepoDigests | Empty array | **GAP — no registry digest; image was built locally and not pushed** |
| Base image | `python:3.11-slim` | **PASS — tag recorded** |
| Base image ID | Empty | **GAP — immutable base-image identity not captured** |
| Base image RepoDigests | Empty | **GAP — immutable base-image digest not captured** |
| Benchmark command | Full command captured in metadata | **PASS** |
| Python runtime | Python 3.11.18 | **PASS — recorded** |
| Source SHA method inside benchmark report | `provided-no-git-metadata` | **CONTEXT — container has no Git metadata; outer workflow independently checked exact checkout SHA** |

The benchmark image RepoDigests being empty is consistent with a local build-only image and no registry push; it is not evidence of a failed benchmark. The missing base-image ID/digest is a reproducibility/provenance gap. Do not invent or infer an immutable base-image digest from the mutable tag. Record this gap for M4/Tech Lead; no M2 AI-code change is indicated.

## 5. Issue #28 acceptance-criteria matrix

| Issue #28 criterion | Evidence reviewed | M5 status |
|---|---|---|
| AI regression tests pass on a named commit SHA | CaroAI CI #41317622027 Python tests/lint job succeeded; benchmark source SHA is pinned. The run summary does not expose a test-by-test tactical report in the artifact. | **PARTIAL — CI green; tactical test-level evidence should be linked/confirmed by M2** |
| Benchmark reruns with documented command and reports median/p95 per difficulty | Exact command, CSV/JSON/Markdown and per-difficulty summary in artifact | **PASS** |
| Linux/Docker uses same source SHA and fixed protocol as Windows evidence; environments separate | Pinned SHA, 11 fixtures, 3 difficulties, 5+1 protocol; separate Linux environment ID | **PASS for Linux/Docker artifact and protocol; Windows comparison remains a separate evidence item** |
| Nearest-rank p95 from 55 measured calls per difficulty; each ≤ 2,000 ms | M5 recalculation from CSV in §3 | **PASS** |
| Zero trial errors; valid output shape; legal moves; unchanged boards; forced-win/forced-block assertions | 165 measured calls valid; two exact tactical demo fixtures pass in all three difficulties | **PASS for benchmark-integrity and named demo assertions** |
| Illegal AI moves are rejected by Backend | Not demonstrated by benchmark artifact; requires a Backend/API negative test or direct CI test reference | **NOT VERIFIED by this artifact** |
| At least three reproducible demo positions | Three fixed fixtures in `reports/ai-demo-boards.json` | **PASS** |
| PR small, reviewed by another member, CI green | CI #41317622027 and E2E #41317622030 green; PR #44 is currently Draft | **PARTIAL — CI green; independent review/ready-for-review still outstanding** |
| M5 completes evidence reconciliation; gaps remain explicit | This reconciliation records raw data, gate results, provenance gaps and boundaries | **PASS for this reconciliation; overall Issue #28 remains open pending remaining owner evidence/sign-off** |

A green benchmark workflow does not, by itself, close all Issue #28 criteria. In particular, the Backend illegal-move rejection criterion and explicit tactical regression-test evidence must be supported by their own tests/references.

## 6. CI and scope boundaries

CaroAI CI #41317622027 completed successfully:
- Python tests and lint;
- PostgreSQL service/API/migration acceptance, including the zero-skipped guard;
- frontend syntax/regression checks;
- disposable Compose persistence after API-container restart;
- Docker image build only.

Browser E2E #41317622030 completed successfully. The approved production publish/Render verification job was **SKIPPED**; no image was published and no production deployment was attempted.

The workflow/benchmark change does not modify AI algorithm code. M5 found no measured benchmark failure that would justify changing M2's AI implementation or M4's workflow. The only identified follow-up is provenance metadata completeness (base-image immutable identity/digest), which should be handled by M4/Tech Lead if required.

## 7. Run 1 disposition and next actions (historical snapshot; superseded by §8)

- **Linux/Docker performance gate:** PASS.
- **Benchmark raw-data integrity and protocol:** PASS.
- **Metadata provenance:** PARTIAL due to missing base-image ID/digest and absent registry digest for the local, unpushed benchmark image.
- **Issue #28 overall:** remains OPEN / not fully accepted until the Backend illegal-move rejection evidence, tactical regression-test references, independent PR review, and M1/Tech Lead sign-off are confirmed.
- **Phase 4 production release:** this benchmark does not establish production readiness or change any separate release blockers.

### Owner follow-up
1. **M4:** if immutable base-image provenance is required, capture the resolved `python:3.11-slim` digest/ID in a future evidence run; do not retroactively invent it.
2. **M2 / Backend owner:** link the named-SHA tactical regression results and Backend illegal-move rejection test evidence.
3. **M1 / Tech Lead:** review this reconciliation and decide whether the remaining provenance gap is acceptable for the Phase 4 benchmark gate.
4. **M5:** keep unverified criteria explicitly NOT VERIFIED until evidence is attached; do not close Issue #28 by inference.

---
*Historical run 1 in this document records artifact #13087737816 from workflow run #41317622028. The latest run 2 reconciliation and updated acceptance disposition are appended below. This document does not alter the benchmark workflow, AI implementation, or production deployment configuration.*


## 8. Evidence refresh — run 2 / artifact #13088582572 (2026-11-01)

This section records the repeat benchmark from M2 and supersedes run 1 only as the latest evidence snapshot. **Run 1 and run 2 remain separate captures**; their samples and percentile values are not pooled.

### 8.1 Evidence identity and workflow result

| Item | Verified value |
|---|---|
| PR / workflow branch | [PR #44](https://github.com/emt0147t/caroAI/pull/44) / `feature/phase4-m4-m5-linux-benchmark` |
| Workflow run | [#41320187247 — SUCCESS](https://github.com/emt0147t/caroAI/actions/runs/41320187247) |
| Workflow job | `Linux Docker benchmark (pinned Phase 4 source)` — completed SUCCESS |
| Artifact | [#13088582572](https://github.com/emt0147t/caroAI/actions/runs/41320187247/artifacts/13088582572) |
| Artifact package digest | `sha256:46827ce44355beff9bd51b8485c26eadaa488a5b71347ab6bbce7c8073ff9d23` |
| Benchmark source SHA | `2b4e3c167d7ca0a2a5b530b7a251ced6dd37d526` |
| Workflow commit SHA in run metadata | `3141c8f21a4d787a913602caef7c87afa815fe05` |
| Benchmark environment ID | `linux-2b4e3c167d7c` |
| Run timestamp | 2026-11-01 15:15 UTC |

The benchmark source SHA and workflow commit SHA are distinct identities. The benchmark rows consistently identify the pinned source SHA; the run metadata separately records the workflow commit SHA. Do not substitute one for the other.

### 8.2 Independent raw-data reconciliation

M5 downloaded and inspected the new artifact contents: `ai-benchmark.csv`, `ai-benchmark.json`, `ai-benchmark.md`, `phase4-gate-evaluation.json`, and `run-metadata.json`.

| Check | Observed | M5 status |
|---|---:|---|
| CSV / JSON raw records | 198 / 198 | **PASS** |
| Exported fields | 22 in each format; 0 row/field mismatches after normalizing JSON booleans/nulls | **PASS** |
| Measured calls | 165 | **PASS** |
| Warm-ups | 33 | **PASS** |
| Fixtures / difficulties | 11 / 3 | **PASS** |
| Per fixture × difficulty | 5 measured + 1 warm-up | **PASS** |
| Source SHA consistency | All 198 records use `2b4e3c167d7ca0a2a5b530b7a251ced6dd37d526` | **PASS** |
| Measured trial errors | 0 | **PASS** |
| Output shape / legal move / unchanged board | 165/165 true for each check | **PASS** |
| Applicable tactical expected-move assertions | 30 true; 0 false | **PASS** |

The 135 blank `expected_move_ok` values are non-applicable generic-fixture rows, not failures. No measured row has an error or a false expected-move assertion.

### 8.3 Run 2 performance results

M5 recalculated nearest-rank p95 from the 55 measured CSV observations per difficulty and cross-checked the result against `phase4-gate-evaluation.json`.

| Difficulty | n | Median (ms) | Nearest-rank p95 (ms) | Maximum (ms) | M1 ceiling | Result |
|---|---:|---:|---:|---:|---:|---|
| EASY | 55 | 3.175035 | 11.994535 | 12.156718 | ≤ 2,000 ms | **PASS** |
| MEDIUM | 55 | 15.742058 | 58.491428 | 58.708514 | ≤ 2,000 ms | **PASS** |
| HARD | 55 | 131.713247 | 490.038169 | 500.080324 | ≤ 2,000 ms | **PASS** |

The 2,000 ms value is the M1-approved Phase 4 Linux/Docker **AI-engine benchmark ceiling per difficulty**. It is not a production SLO, HTTP/API latency target, or end-to-end service guarantee.

### 8.4 Run 1 versus run 2 — separate snapshots

| Run | Artifact | EASY p95 (ms) | MEDIUM p95 (ms) | HARD p95 (ms) | Gate |
|---|---|---:|---:|---:|---|
| Run 1 — #41317622028 | [#13087737816](https://github.com/emt0147t/caroAI/actions/runs/41317622028/artifacts/13087737816) | 6.418816 | 30.346136 | 255.984226 | **PASS** |
| Run 2 — #41320187247 | [#13088582572](https://github.com/emt0147t/caroAI/actions/runs/41320187247/artifacts/13088582572) | 11.994535 | 58.491428 | 490.038169 | **PASS** |

Both runs use the same pinned benchmark source SHA and fixed 11-fixture / 3-difficulty / 5-measured + 1-warm-up protocol. Their captured timings differ and remain separate; do not average or pool the observations. The repeat run's p95 is higher in all three difficulty groups but remains comfortably below the approved ceiling.

### 8.5 Run 2 environment and provenance

| Metadata | Captured value | M5 assessment |
|---|---|---|
| Runner | Linux / X64; AMD EPYC 7763 64-Core Processor; 4 host vCPUs online | **RECORDED** |
| Docker server | 28.0.4 | **RECORDED** |
| Container limits | `--cpus=2 --memory=4g` | **RECORDED** |
| Benchmark image ID | `sha256:4fcae654ac9ec2ef8ded06218cf4c21a7893a0536cc22932884a3e671c89fc32` | **RECORDED** |
| Benchmark image RepoDigests | Empty | **PROVENANCE GAP** — locally built image was not pushed to a registry |
| Base image tag | `python:3.11-slim` | **RECORDED** |
| Base image ID / RepoDigests | Empty / empty | **PROVENANCE GAP** — immutable base-image identity/digest not captured |
| Python | 3.11.18 | **RECORDED** |
| Source SHA method inside container | `provided-no-git-metadata` | **CONTEXT** — outer workflow checks out/verifies the pinned source revision |

The base-image digest and benchmark-image RepoDigest must not be invented or inferred. The benchmark image ID and all other captured metadata remain recorded. PR #44's M1 disposition accepts this provenance limitation as documented for the Phase 4 benchmark gate; it does **not** establish fully immutable base-layer reproducibility. Future benchmark workflows should pin the base image by digest if stronger provenance is required.

The artifact's `ai-benchmark.md` / `ai-benchmark.json` legacy summary field still says `PENDING_TEAM_CONFIRMATION`; the run's `phase4-gate-evaluation.json` explicitly records the M1 decision dated 2026-11-01 and independently reports the gate PASS. The gate-evaluation decision is the controlling acceptance evidence; the stale legacy summary field should be normalized by the workflow owner in a future metadata cleanup, not silently represented as a new M1 decision.

### 8.6 Backend negative-test source evidence supplied by M2

The following test definitions were independently opened at exact commit `83a8c5f87209d84c0cb12beea02a12e20dd23357`:

- [`tests/test_ai_integration.py` lines 73–88](https://github.com/emt0147t/caroAI/blob/83a8c5f87209d84c0cb12beea02a12e20dd23357/tests/test_ai_integration.py#L73-L88): `test_ai_service_rejects_illegal_ai_move` monkeypatches an AI move onto an occupied cell, expects `InvalidAIMoveError`, and verifies the game state remains unchanged.
- [`tests/test_ai_integration.py` lines 184–220](https://github.com/emt0147t/caroAI/blob/83a8c5f87209d84c0cb12beea02a12e20dd23357/tests/test_ai_integration.py#L184-L220): malformed and out-of-bounds AI output cases expect `InvalidAIMoveError`.
- [`tests/test_games_api.py` lines 187–220](https://github.com/emt0147t/caroAI/blob/83a8c5f87209d84c0cb12beea02a12e20dd23357/tests/test_games_api.py#L187-L220): API-level illegal AI move returns HTTP 400 and an `already occupied` detail.

**M5 source review: PASS — the Backend negative-test definitions exist at the referenced SHA. Execution evidence: PENDING M2** until M2 attaches the actual pytest command, branch/SHA, test counts and exit status from its rerun. A source link alone is not proof that the tests ran. The same pending execution evidence applies to the named-SHA tactical regression acceptance criterion.

### 8.7 Updated Issue #28 acceptance disposition

| Criterion | Updated M5 status | Evidence / remaining condition |
|---|---|---|
| AI tactical regression tests pass on named SHA | **PARTIAL — execution pending** | M2's actual pytest rerun and named SHA/result summary have not yet been supplied |
| Reproducible benchmark command and per-difficulty median/p95 | **PASS** | Run 1 and run 2 artifacts; run 2 command and raw CSV/JSON reviewed |
| Linux/Docker fixed protocol and pinned source SHA | **PASS** | Both runs use the same source SHA and 11 × 3 × (5 + 1) protocol; Linux remains separate from Windows |
| Nearest-rank p95 ≤ 2,000 ms for every difficulty | **PASS** | Run 2: 11.994535 / 58.491428 / 490.038169 ms |
| Zero measured errors; valid shape/legal moves/unchanged board; expected tactical assertions | **PASS** | Run 2: 165/165 structural checks, zero errors, 30 applicable expected assertions true |
| Backend rejects illegal AI moves | **PARTIAL — source coverage verified; execution pending** | Three test references verified at commit `83a8c5f...`; await M2 pytest execution result |
| At least three reproducible demo positions | **PASS** | `demo_ai_win_now`, `demo_forced_block`, `demo_midgame_search` |
| PR reviewed and CI green | **PASS for PR #44 lifecycle/review** | PR #44 merged; independent review APPROVED by KenKen106. This does not validate production deployment |
| Provenance completeness | **PARTIAL / accepted limitation** | Benchmark image ID recorded; benchmark RepoDigest and base-image immutable ID/digest absent; M1 disposition accepted the documented gap for this gate |
| Overall Issue #28 | **OPEN — M2 execution evidence pending** | Do not close until actual pytest results are attached and M1/Tech Lead completes the remaining Issue #28 closeout |

### 8.8 Current M5 disposition and owner actions

- **Linux/Docker benchmark performance gate:** PASS on both separate runs.
- **Run 2 raw-data integrity:** PASS; independently reconciled 198 CSV/JSON records and all 165 measured calls.
- **Backend negative-test source coverage:** verified; actual M2 pytest execution result is still pending.
- **Tactical regression test execution:** pending M2's named-SHA pytest evidence.
- **Provenance:** documented limitation accepted for this Phase 4 gate; future digest pinning remains a quality improvement.
- **Production release:** this benchmark does not change separate release blockers or establish production SLO/API latency.

Owner follow-up:
1. **M2 / Backend owner:** attach the actual pytest command, exact branch/SHA, test counts and exit status for the referenced Backend negative tests and tactical regression tests.
2. **M4:** consider pinning `python:3.11-slim` by immutable digest and recording resolved base-image identity in a future benchmark workflow; no retroactive value should be fabricated.
3. **M1 / Tech Lead:** complete Issue #28 closeout after reviewing M2's execution evidence; do not treat benchmark PASS alone as full Issue #28 acceptance.
4. **M5:** keep execution-dependent criteria PARTIAL until M2's run evidence is attached.

---
*Run 2 is the latest M5 reconciliation snapshot for artifact #13088582572 / workflow #41320187247. Run 1 remains preserved above as historical evidence; the two result sets are not pooled. No workflow, AI implementation, or deployment configuration was modified by this update.*


## 9. Final Issue #28 closeout reconciliation — 2026-11-01

This section supersedes the earlier provisional Issue #28 status in §§5, 7 and 8.6–8.8. Those passages accurately recorded the evidence state before M2 supplied the final regression evidence and M1/Tech Lead completed closeout; they are retained as historical checkpoints, not the current disposition.

**Current authoritative disposition: Issue [#28](https://github.com/emt0147t/caroAI/issues/28) is CLOSED / COMPLETE (2026-11-01).** The final issue record states that all acceptance criteria for the AI tactical-regression and benchmark scope are met and records M1/Tech Lead sign-off as **ACCEPTED WITH DOCUMENTED PROVENANCE LIMITATION**.

| Acceptance item | Final disposition | Evidence recorded in Issue #28 |
|---|---|---|
| AI tactical regression | **PASS** | M2 targeted AI regression suite: 59 passed on source SHA `83a8c5f87209d84c0cb12beea02a12e20dd23357`; full suite: 238 passed, 11 skipped, 1 warning. The 11 skips require `TEST_DATABASE_URL` and are not counted as passes. |
| Backend illegal-output rejection | **VERIFIED / ACCEPTED** | Service/API negative-test definitions are linked at the named source SHA; Issue #28's final acceptance section records Backend illegal-output rejection as verified. |
| Linux/Docker benchmark | **PASS** | Canonical run #41317622028 and repeat run #41320187247; raw-data and per-difficulty p95 reconciliation retained in §§1–4 and §8. |
| p95 acceptance ceiling | **PASS — scoped** | M1 adopted ≤ 2,000 ms independently per difficulty as the Phase 4 Linux/Docker AI-engine benchmark ceiling only; it is not a production SLO or API latency target. |
| Provenance | **ACCEPTED WITH DOCUMENTED LIMITATION** | Missing immutable base-image ID/digest and empty local benchmark-image RepoDigests remain disclosed; M1 accepted this limitation for Issue #28. No digest is inferred. |
| Issue #28 closeout | **CLOSED / COMPLETE** | M1/Tech Lead final sign-off recorded in the issue body; state is closed with completed disposition. |

The earlier “pytest execution pending” and “Issue #28 remains open” statements are superseded by this final issue-level acceptance. This update does not claim a new independent pytest run by M5; it records M2's supplied results and M1/Tech Lead's final acceptance.

**Scope boundary:** Issue #28 closeout completes only the AI tactical-regression and benchmark scope. It does not approve production deployment, establish a production SLO, or close the separate Phase 4 release blockers. Overall production release remains **BLOCKED / NO-GO** until its own gates are satisfied.

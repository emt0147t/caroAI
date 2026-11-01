# Phase 4 M5 — Linux/Docker AI Benchmark Reconciliation

**Reconciliation date:** 2026-11-01  
**Scope:** PR #44 / Issue #28 — independent M5 review of the Linux/Docker benchmark artifact.  
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

## 7. M5 disposition and next actions

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
*This document records M5's independent reconciliation of artifact #13087737816 from workflow run #41317622028. It does not alter the benchmark workflow, AI implementation, or production deployment configuration.*

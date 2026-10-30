# Phase 4 — M5 D-stage evidence register

> Updated: 2026-10-30  
> Branch: `feature/m5-sprint4-qa`  
> PR: [#39](https://github.com/emt0147t/caroAI/pull/39) — open, unmerged  
> Purpose: evidence coordination and layer-by-layer acceptance. This document is not production approval.

## 1. Evidence rules

- Every result is scoped to the exact source SHA, workflow, browser/runtime, URL and environment actually used.
- Keep PR head SHA separate from a merge-validation SHA.
- `PASS` means the specific layer was tested and the created game's expected state was read back. It does not imply another layer passed.
- `PARTIAL` means there is relevant automated evidence, but the complete criterion or metadata is missing.
- `NOT RUN` means no execution evidence is available. `BLOCKED` means a named dependency prevents execution.
- A successful `/health` or `/ready` response is not persistence evidence.
- Use only designated non-personal test games for public smoke. Never post credentials, tokens, database URLs, or personal data.

## 2. Browser E2E — current PR/CI evidence

### Run identity

| Field | Recorded value |
|---|---|
| Workflow | [Frontend Browser E2E run #40911314445](https://github.com/emt0147t/caroAI/actions/runs/40911314445) |
| Result | **SUCCESS** — browser-e2e job completed successfully |
| PR head SHA | `0aba6de5acbcf3c67260b09dad00e96292d314bd` |
| Base SHA | `138164803f3537d15ca90d9bc358f3f86528c4f3` |
| Merge-validation SHA | `1a633614d0a37790e6ca0cd11a5def797c29a607` |
| Environment / URL | Disposable CI Compose stack; proxied app at `http://127.0.0.1:8080` |
| Browser | Chromium via Playwright; exact Chromium build/version **NOT RECORDED in current evidence summary** |
| Test result | **13 Playwright tests passed** (per verified run record) |
| Artifact | [Playwright evidence artifact #12913244100](https://api.github.com/repos/emt0147t/caroAI/actions/artifacts/12913244100), SHA-256 `1783f4226551b12ba7669162ef47f48197bad12c1329d3e0a79f6e14333cc6c0` |
| Scope | PR/CI only; not a public deployment |

The workflow installs Playwright and Chromium, starts the real API and frontend, waits for the proxied API, runs the browser suite, uploads evidence and tears down the stack. The M3 E2E guide states that History reads `GET /api/history?limit=20&offset=0` from the backend and does not use mock/localStorage history. The persistence test creates a real game, verifies it in API History, opens a fresh page and reloads to confirm the same record remains visible. A missing History endpoint must fail the test; the persistence test is not skipped on 404. See [M3 E2E/History guide](./sprint3-m3-e2e-history.md).

### Acceptance coverage register

| Check | Current assessment | Evidence / gap |
|---|---|---|
| PvP flow | **PASS — PR/CI only** | Included in the 13-test Browser E2E run; repeat on approved public candidate. |
| PvAI flow | **PASS — PR/CI only** | Real API/backend flow covered in Browser E2E; this does not establish AI tactical quality or benchmark performance. |
| Difficulty passed correctly | **PARTIAL — PR/CI only** | PvAI flow is covered; M3 to confirm the test asserts the exact selected difficulty in the backend request/payload. |
| AI move returned by backend | **PASS — PR/CI only** | PvAI test exercises the real API flow. Keep this distinct from tactical benchmark/T-12. |
| Double-submit prevention | **PASS — PR/CI only** | Included in the current E2E coverage record. |
| API error displayed/handled | **PASS — PR/CI only** | HTTP 400/422/404 and error-state coverage recorded; public API behavior remains untested. |
| Lost-response safe recovery | **PASS — PR/CI only** | Network recovery and AI retry scenarios recorded; injected network failures are browser-boundary simulations, not production outages. |
| Win/loss/draw and post-game lock | **PARTIAL — PR/CI only** | Win/terminal lock and draw scenarios recorded; confirm explicit loss assertion and complete terminal-state matrix with M3. |
| History uses real API, not mock/localStorage | **PASS — PR/CI only** | M3 guide documents backend `GET /api/history`, fresh-page and reload read-back; no localStorage history. |
| Missing/failing History endpoint fails test, not skip | **PASS by test contract; re-confirm on current artifact** | M3 guide explicitly says persistence assertion is not skipped on 404. M3 to attach test/log excerpt from current run. |
| Refresh/reload | **PASS — PR/CI only** | Same created game remains visible after a fresh page/reload. |
| Desktop/mobile viewport | **PASS — PR/CI only** | Desktop/mobile viewport scenario included in current 13-test coverage record. |
| Browser/version metadata | **PARTIAL** | Chromium is installed; exact version/build is not recorded in this evidence register. M3 to supply exact version from workflow log/artifact. |
| Public browser smoke | **NOT RUN** | No approved public URL and deployed image SHA supplied. |

**M3 action:** confirm the rows marked PARTIAL, and provide exact browser version/build, base URL, timestamp, named test outcomes, and artifact reference. Do not mark public smoke PASS based on this CI run.

## 3. Persistence — independent layers

A PASS requires the same game created before the boundary to be read back afterwards, with its game ID and expected moves/history/state recorded.

| Layer | Status | Evidence / limitation |
|---|---|---|
| New DB session / service instance | **PASS in automated DB/API acceptance scope; candidate-scoped** | PostgreSQL service/API/migration acceptance in [CI run #40911314962](https://github.com/emt0147t/caroAI/actions/runs/40911314962) passed. Existing repository/API persistence tests exercise read-back via a new session/service boundary. Record the exact test/game identifier from logs before treating this as a named manual scenario. |
| API restart in disposable Compose | **PASS — CI only** | Job “Compose API/database persistence after restart” in [CI run #40911314962](https://github.com/emt0147t/caroAI/actions/runs/40911314962) passed. The job creates a game/move, restarts the API container, then reads the persisted state. Disposable CI DB/Compose only. |
| Browser refresh / fresh page | **PASS — PR/CI only** | [Browser E2E #40911314445](https://github.com/emt0147t/caroAI/actions/runs/40911314445): History reads the same created game after fresh page/reload. This proves browser/API read-back in CI, not production durability. |
| Production restart/redeploy | **NOT RUN / BLOCKED** | Production publish/deploy job in CI #40911314962 was **SKIPPED**. No approved release URL, live image identity or production redeploy evidence is available. Owner: M4 Vinh; M1 validates persistence semantics; M5 audits. |

### Related CI gates (do not conflate)

- PostgreSQL service/API/migration acceptance: **15 passed, 0 skipped**, explicit zero-skip guard passed in [CI run #40911314962](https://github.com/emt0147t/caroAI/actions/runs/40911314962).
- Compose API/database persistence after restart: **SUCCESS** in the same run.
- Docker image build: **SUCCESS**, build only; no publish/deploy.
- Approved production publish and Render verification: **SKIPPED**.
- These workflows were associated with PR head `0aba6de5acbcf3c67260b09dad00e96292d314bd`; the PR validation snapshot was merge commit `1a633614d0a37790e6ca0cd11a5def797c29a607`. Do not attribute a result to a different SHA.

## 4. Public smoke and production deployment

| Requirement | Status | Required evidence / owner |
|---|---|---|
| Public HTTPS URL | **BLOCKED** | M4 supplies approved public base URL and environment. |
| `/health` | **NOT RUN** | M4 executes after approved deployment; capture timestamp/status/body. |
| `/ready` | **NOT RUN** | M4 executes after approved deployment; capture DB readiness response. Neither endpoint alone proves persistence. |
| Public PvP | **NOT RUN** | M3 executes on public URL; M1 validates API/state; M5 records. |
| Public PvAI | **NOT RUN** | M3 executes; M1/M2 validate backend AI behavior; M5 records. |
| Public History | **NOT RUN** | M3 verifies real API-backed History; M1 validates contract. |
| Public reload | **NOT RUN** | M3 reloads and verifies the same test game/history. |
| Game survives production redeploy | **NOT RUN / BLOCKED** | M4 performs only after approval; M1 validates; M5 verifies same game ID and moves/history before/after. |
| Published image full SHA/digest | **NOT RUN** | M4 provides immutable image identity matching approved source SHA. |
| Deployment ID/status | **NOT RUN** | M4 provides deployment identifier, live status and deployed image reference. |

**No deployment is authorized by this QA request.** If production access, environment approval, or an approved release candidate is missing, keep these rows `NOT RUN`/ `BLOCKED`, state the reason and owner, and do not dispatch a deployment.

### Public smoke safety

- Use a designated synthetic/non-personal test game only.
- Record game ID, creation timestamp, source SHA, image SHA/digest, deployment ID/status, public URL, browser/version, and redacted screenshots/traces.
- Do not post secrets, tokens, database credentials, private deploy hooks, or personal game content in issues/artifacts.
- After redeploy, verify the exact same game ID and expected moves/history; a healthy endpoint is not sufficient.

## 5. Owner coordination

- **M3 Hiền (@NgocHein):** confirm Browser E2E coverage and missing metadata listed in Section 2; supply artifact/log excerpts and later execute public PvP/PvAI/History/reload smoke when M4 supplies approved URL and release identity.
- **M4 Vinh (@macvinh2007-sketch):** update [Issue #30](https://github.com/emt0147t/caroAI/issues/30) with approved public HTTPS URL, source SHA, image full SHA/digest, deployment ID/status, health/readiness results, and production before/after test-game persistence evidence. Do not deploy without approval.
- **M1 Thành (@emt0147t):** validate History/API contract and persistence semantics; independently review release evidence.
- **M5 Hiếu (@dyhieu-vu):** maintain this matrix, verify exact SHA/layer linkage, and keep release status BLOCKED until all required evidence and independent review exist.

Coordination request posted once on [Issue #31](https://github.com/emt0147t/caroAI/issues/31) on 2026-10-30. M3/M4 acknowledgement and execution evidence are pending.

## 6. Current Phase D decision

- Browser E2E: **PASS at PR/CI scope**, with exact browser version and a few assertion-level confirmations pending from M3.
- Compose API restart: **PASS at disposable CI scope**.
- New DB session/API read-back: **PASS in automated DB/API acceptance scope**, with exact test identifier/log excerpt to be attached for traceability.
- Browser refresh: **PASS at PR/CI scope**.
- Production persistence after redeploy: **NOT RUN / BLOCKED**.
- Public smoke: **NOT RUN / BLOCKED**.
- Overall release: **BLOCKED / NO-GO**.

This Phase D register is an evidence-coordination artifact, not production acceptance or deployment authorization.


## 7. Latest verification addendum — PR #39 head e349bb9

> This addendum supersedes older Browser E2E / CI counts and assertion-level gaps above for the exact head SHA recorded here. Earlier runs remain historical evidence only.

| Field | Latest verified value |
|---|---|
| PR | [#39](https://github.com/emt0147t/caroAI/pull/39), still open and unmerged |
| Exact PR head SHA | `e349bb9a4cc8981371bba4efeaba57b4d7cb6043` |
| CaroAI CI | [Run #40992816484](https://github.com/emt0147t/caroAI/actions/runs/40992816484) — **SUCCESS** |
| Frontend Browser E2E | [Run #40992816602](https://github.com/emt0147t/caroAI/actions/runs/40992816602) — **SUCCESS** |
| Browser E2E job | All workflow steps completed successfully, including browser setup, version capture, real API/frontend startup, E2E run, artifact upload and stack teardown |
| Playwright | **1.56.1** |
| Chromium | **141.0.7390.37** (Playwright build v1194) |
| Browser suite | **14 passed, 0 failed**, 2 workers, 10.6 seconds |
| Artifact | [Playwright evidence #12949728249](https://github.com/emt0147t/caroAI/actions/runs/40992816602/artifacts/12949728249), SHA-256 `7ae20c9434d6f31aa760f59e1338d6e2c9849ba132e86b28804ed15450579b2a` |
| Browser base URL | Disposable CI Compose stack, `http://127.0.0.1:8080`; not public production |

### Newly closed Browser E2E gaps

- **Difficulty payload — PASS:** PvAI hard-mode test captures the actual POST `/api/games/{id}/ai-move` request and asserts the submitted `difficulty` is `hard`.
- **O-win / losing-X lock — PASS:** test drives a real PvP game through O's five-in-a-row, asserts UI message `O thắng!`, verifies all board cells are disabled, and reads backend state asserting `status=O_WON`, `winner=O`, `move_count=10`.
- **History — PASS in CI:** real API history, fresh-page/reload behavior and error/retry test all passed in the 14-test suite.
- **Full suite — PASS:** all 14 named browser tests passed, including PvP, PvAI, difficulty payload, duplicate-submit prevention, HTTP 400/422/404 handling, recovery/retry, terminal lock, O win, draw and responsive viewport.

### Latest CaroAI CI job results

| Job | Result |
|---|---|
| Frontend syntax and regression checks | **SUCCESS** |
| PostgreSQL service/API/migration acceptance | **SUCCESS**; explicit zero-skipped-test guard passed |
| Python tests and lint | **SUCCESS**; pytest output: **226 passed, 11 skipped, 1 warning** |
| Compose API/database persistence after restart | **SUCCESS**; created a game and move, restarted the API container, then read back the same game's move count, board, current player and History record |
| Docker image build (no publish/deploy) | **SUCCESS**; build only |
| Approved production publish and Render verification | **SKIPPED** |

The PostgreSQL acceptance job reported: “PostgreSQL acceptance suite completed with zero skipped tests.” The separate general Python suite's 11 skips are not PostgreSQL acceptance skips and must not be conflated with that explicit DB guard.

### Updated Phase D assessment for this SHA

- Browser E2E, including difficulty payload, O-win terminal behavior, History, refresh and responsive viewport: **PASS — PR/CI scope**.
- Compose API restart and PostgreSQL persistence/read-back: **PASS — disposable CI scope**.
- General Python/lint and frontend regression: **PASS — CI scope**.
- Docker image build: **PASS — build only; no publish**.
- Public HTTPS smoke, live deployment identity, production redeploy persistence and rollback: **NOT RUN / BLOCKED**; production publish/deploy workflow was skipped.
- PR #39 remains open/unmerged. These results do not approve deployment or establish production acceptance. Overall release remains **BLOCKED / NO-GO** until the independent release gates and PR #35 History contract disposition are closed.


## 8. Release-gate reconciliation snapshot — GitHub check 2026-10-30

M5 checked the live GitHub issue/PR records for T-12, T-14–T-17 and the History contract. No new owner-provided benchmark, approved release-candidate identity, public endpoint, production persistence, or rollback evidence was present in the records at the time of this check. Do not infer execution from issue descriptions or CI-only results.

| Gate | Owner / source checked | Evidence currently visible | M5 disposition |
|---|---|---|---|
| T-12 — AI tactical regression + Linux/Docker benchmark | M2 Kiên (@KenKen106), [Issue #28](https://github.com/emt0147t/caroAI/issues/28) | Issue remains **OPEN**. No owner artifact/comment with exact tested SHA, tactical regression outcomes, reproducible Docker command/environment/CPU limits, fixtures/trials/warm-up, raw CSV/JSON, easy/medium/hard median+p95, or M1/team SLO decision was present. M5's evidence request remains the latest comment. | **BLOCKED / EVIDENCE NOT SUPPLIED**. M2 owns test/benchmark artifacts; M4 supports comparable Docker/CPU environment; M1/team must explicitly decide whether p95 ≤ 2,000 ms is the target/SLO. Do not label the proposed threshold accepted. |
| T-13 — approved RC and immutable image identity (dependency for public gates) | M4 Vinh, M1 reviewer, [Issue #30](https://github.com/emt0147t/caroAI/issues/30) | No approved public HTTPS URL, approved source SHA, published image full SHA/digest, deployment ID/status, or release approval was visible. Production publish/deploy remained skipped in the latest verified CI. | **BLOCKED**. Public smoke must not start without approved RC and deployment identity. |
| T-14 — public HTTPS health/readiness | M4, Issue #30 | No public URL or timestamped /health and /ready result supplied. | **NOT RUN / BLOCKED**. M4 executes only after release approval and environment authorization. Health/readiness alone is not persistence evidence. |
| T-15 — public PvP/PvAI/History smoke | M3 Hiền (@NgocHein), M4, Issue #30 | M3's latest visible comment (2026-10-23) says NOT RUN pending HTTPS RC URL plus deployed image/release SHA; M3 will not change deployment/proxy/backend configuration independently. Latest Browser E2E is disposable CI only. | **NOT RUN / BLOCKED**. M3 executes on the approved public candidate once M4 supplies URL and immutable image/source identity; M1 validates API/state; M5 records. Do not ask M3 to run against an unidentified deployment. |
| T-16 — same-game persistence after production redeploy | M4 executes; M1 validates; M5 audits, Issue #30 and [Issue #31](https://github.com/emt0147t/caroAI/issues/31) | No designated synthetic game's ID and before/after production read-back across a real redeploy was supplied. Compose restart and browser refresh evidence are separate CI layers and do not satisfy this gate. | **NOT RUN / BLOCKED**. Require same game ID, expected moves/board/status/History before and after approved redeploy, plus source/image SHA and deployment ID. |
| T-17 — rollback/redeploy | M4 executes; M1 independently reviews; M5 audits, Issue #30 | No rollback execution record, old/new immutable image identities, deployment IDs/statuses, health/readiness, or post-rollback persistence read-back was supplied. | **NOT RUN / BLOCKED**. Require approved rollback procedure and traceable before/after deployment evidence; no deployment action is authorized by this audit. |
| History contract — PR #35 | M1 Thành (@emt0147t), [PR #35](https://github.com/emt0147t/caroAI/pull/35) | PR #35 is still **OPEN, DRAFT, UNMERGED**, targets main, and adds an in-memory History implementation. M1's 2026-10-29 comment explicitly says not to merge as-is: current develop already has routes_history.py and GameService.list_history() backed by configured repository/SQLAlchemy persistence. M1 recommends closing as superseded if no independent fix exists, or reproducing a real defect on current develop and submitting a small fix based on develop. | **CONTRACT BASELINE: persisted History on current develop. FORMAL PR DISPOSITION: PENDING M1**. M5 must not close PR #35 or claim it formally superseded without M1/maintainer action. Any actual defect must be reproduced on current develop with a regression test; do not transplant the old in-memory implementation. |

### Coordination / next owner actions

1. **M2:** attach the T-12 benchmark package to Issue #28, or explicitly mark unrun sub-items with reasons. Include raw machine-readable results and the full source SHA.
2. **M1 + M2:** record an explicit decision on the proposed p95 ≤ 2,000 ms threshold (target/SLO, or rejected/replaced with rationale).
3. **M4 + M1:** update Issue #30 with release approval, RC source SHA, immutable image digest, deployment ID/status, public URL and timestamped health/readiness. Do not publish/deploy merely to satisfy this checklist.
4. **M3:** once M4's approved URL and image/source identity exist, execute public PvP/PvAI/History/reload smoke and attach named results/artifacts.
5. **M4 + M1:** execute and independently validate production same-game persistence across redeploy and rollback only under approved release/change control.
6. **M1/maintainer:** record the formal PR #35 disposition (close as superseded, or identify a current-develop defect and open a minimal corrective PR).
7. **M5:** update this register only when linked evidence is available; retain NOT RUN/BLOCKED for absent production evidence.

**Current release decision remains BLOCKED / NO-GO.** Browser E2E, PostgreSQL acceptance, Compose restart, and image build passed at CI scope on the recorded PR SHA. They do not close T-12–T-17 or grant deployment approval.

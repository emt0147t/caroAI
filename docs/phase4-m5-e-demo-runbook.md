# Phase 4 — M5 seven-minute demo runbook

> Prepared: 2026-10-30. This is a reproducible runbook, not a claim that a presenter workstation has been exercised.
> Current disposition: **BLOCKED / NO-GO**.
> Candidate evidence head: 5ca2766f35a2ec54dba393e417074246683bdb60.
> Related: [QA matrix](phase4-m5-qa-matrix.md) · [D-stage evidence](phase4-m5-d-evidence.md) · [Release sign-off](phase4-m5-e-release-signoff.md).

## 1. Demo rules

- State the environment and exact source SHA before showing the application.
- Use synthetic, non-personal game data only.
- Never invent AI moves, History records, match outcomes, benchmark values, public URLs, image digests, Render status, or persistence results.
- Local Compose restart is not a production redeploy.
- If a step cannot be demonstrated, say NOT RUN or NOT VERIFIED and continue; never substitute a mock or screenshot.
- Do not display secrets, tokens, database URLs, deployment hooks, or unredacted logs.

## 2. Presenter preflight (before the seven-minute clock)

From the repository root, for a local development environment only:

1. Copy .env.example to .env and replace the sample PostgreSQL password with a local-only value. Never put production credentials in .env.
2. Start the stack:
   
       docker compose up --build -d
       docker compose ps

   The API container runs the versioned migration runner before Uvicorn. Compose waits for PostgreSQL health and API /ready.
3. Check application liveness and database readiness:
   
       Invoke-RestMethod http://localhost:8000/health
       Invoke-RestMethod http://localhost:8000/ready

4. Open the frontend at http://localhost:8080 and OpenAPI at http://localhost:8000/docs.
5. Confirm a fresh synthetic game can be created.

If Docker, PostgreSQL, migrations, or the app is not ready, use the troubleshooting section and do not pretend the demo is live.

## 3. Seven-minute flow

| Time | Segment | Presenter actions and evidence | Limitation to state |
|---|---|---|---|
| **00:00–00:30** | Introduce CaroAI and modes | Identify build SHA/environment. Explain 15×15 Caro, PvP/PvAI, FastAPI and PostgreSQL-backed API. | Local/Compose is not public production. |
| **00:30–02:00** | PvP | Start Human vs Human. Play alternating X/O moves. Show turn switching and authoritative board state. Optionally show GET /api/games/{game_id}. | Claim win/draw only when UI and API confirm it. |
| **02:00–03:30** | PvAI and difficulty | Start Human vs AI, select a difficulty, make a human move, wait for the real backend AI response, and show the returned board/current player. | E2E verifies the hard difficulty payload reaches the real API on its tested snapshot. Tactical benchmark and latency SLO are not accepted; do not claim AI quality or speed. |
| **03:30–04:30** | History, refresh and persistence | Open History, identify the synthetic game, refresh/reopen, and compare the same game ID and move count. Optionally query GET /api/history?limit=20&offset=0. | This proves only the environment being shown. Browser refresh, Compose restart and production redeploy are separate layers. |
| **04:30–05:30** | OpenAPI, readiness, PostgreSQL, Compose, E2E and benchmark | Show /docs, /health and /ready. Explain /health is liveness and /ready runs SELECT 1 against the configured DB. Open the workflow links below. | CI is green on the recorded SHA. Sprint 3 Linux/Docker AI benchmark and M1/team latency target/SLO decision are not evidenced. Sprint 2 Windows measurements are not a substitute. |
| **05:30–06:30** | Public URL, image SHA, Render and post-redeploy persistence | Show only if M4 supplies approved HTTPS URL, immutable image digest, deployment ID/status and timestamped health/readiness. Show same-game before/after read-back only if recorded. | **NOT RUN / BLOCKED.** No verified public URL, live image digest, deployment ID, public smoke or production redeploy persistence evidence is recorded. Do not substitute localhost. |
| **06:30–07:00** | Limitations and next steps | Show release sign-off and issue triage. State remaining owner actions: M2 benchmark, M4 approved release/deployment, M3 public smoke, M1 History contract decision/independent review. | Overall release remains **BLOCKED / NO-GO**. |

## 4. Verified workflow links

Both current PR #39 workflows completed successfully on exact head 5ca2766f35a2ec54dba393e417074246683bdb60:

- [CaroAI CI #40993819096](https://github.com/emt0147t/caroAI/actions/runs/40993819096) — SUCCESS. PostgreSQL acceptance/zero-skip guard, frontend regression, Compose API/database persistence after restart, Python tests/lint and Docker image build succeeded. Production publish/Render verification was skipped.
- [Frontend Browser E2E #40993819081](https://github.com/emt0147t/caroAI/actions/runs/40993819081) — SUCCESS. Browser setup, version capture, real API/frontend startup, E2E, artifact upload and teardown completed.
- [Playwright artifact #12950163434](https://github.com/emt0147t/caroAI/actions/runs/40993819081/artifacts/12950163434).

These are PR/CI results, not public production checks. The detailed 14/14 Browser E2E result and browser versions are recorded against their own exact SHA in the D-stage evidence register; do not silently transfer counts to another SHA.

## 5. Optional API proof commands (local Compose only)

Run in PowerShell after the stack is healthy:

    $game = Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/games" -ContentType "application/json" -Body '{"mode":"HUMAN_VS_HUMAN"}'
    $game.id
    Invoke-RestMethod -Method Post -Uri "http://localhost:8000/api/games/$($game.id)/moves" -ContentType "application/json" -Body '{"row":7,"col":7}'
    Invoke-RestMethod "http://localhost:8000/api/games/$($game.id)"
    Invoke-RestMethod "http://localhost:8000/api/history?limit=20&offset=0"

To demonstrate the Compose API-restart layer only:

    docker compose restart app
    Invoke-RestMethod "http://localhost:8000/api/games/$($game.id)"
    Invoke-RestMethod "http://localhost:8000/api/history?limit=20&offset=0"

Compare game ID, move count, board and History entry. Do not call this production redeploy evidence. Avoid docker compose down -v when retaining the local DB volume.

## 6. If a step fails

Capture exact source SHA, environment, command, expected/actual result, sanitized logs and workflow/artifact URL. Add a record using [Failure triage](phase4-m5-e-failure-triage.md). Do not hide a failure by substituting mocks, deleting assertions, skipping tests or retrying until a misleading green result appears.

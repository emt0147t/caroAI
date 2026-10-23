# Sprint 3 M3 browser E2E and history UI

## Browser-driven E2E

Requirements: Docker Desktop / Docker Engine with Compose v2, Node.js 20+, npm.

From the repository root:

```sh
docker compose up -d --build
npm install
npx playwright install chromium
npm run test:e2e
docker compose down -v
```

The tests use Chromium and the real Compose-served frontend/API at `http://127.0.0.1:8080`. PvP/PvAI success paths call the actual API. Network faults and HTTP error codes are deliberately injected at the browser network boundary to verify UI recovery; those cases are not claimed as backend-generated faults. Playwright writes traces, screenshots, video on failure under `test-results/`.

CI workflow: `.github/workflows/frontend-e2e.yml`. The job starts Compose, waits for the same-origin proxied `/health` endpoint, runs Playwright, uploads evidence as a workflow artifact and tears down the stack.

## History UI and API dependency

The History page at `/history.html` never reads or writes game history in localStorage. It requests `GET /api/games/history?limit=20&offset=0`, renders backend items, and provides loading, empty, error and retry states. The UI accepts a raw array or an `items`/`games` array envelope.

**Dependency:** as of this branch creation, the develop API does not expose the history endpoint. A coordination request is recorded on Issue #23 asking M1 to confirm the path and response contract. The page therefore reports the endpoint as unavailable instead of fabricating records. The persistence E2E is explicitly skipped while the endpoint returns 404; it becomes an API-backed refresh/reopen assertion once M1 ships the agreed endpoint. Replay of individual moves is not implemented because no moves-detail/replay endpoint has been confirmed.

## Public deployment smoke

Not run in this change: Issue #30 (M4) remains open and no confirmed HTTPS release URL/release SHA is provided in the repository coordination records. Do not treat localhost CI as public deployment evidence. Once M4 publishes a URL and release SHA, run the same Playwright suite against the deployment after confirming that its API contract matches this branch; capture URL, browser/version, UTC timestamp, release SHA, screenshots/traces and result.

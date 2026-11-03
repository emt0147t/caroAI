# Sprint 3 M3 browser E2E and history UI

## Browser-driven E2E

Requirements: Docker Desktop / Docker Engine with Compose v2, Node.js 20+, npm.

From the repository root:

```sh
docker compose up -d --build
npm ci
npx playwright install chromium
npm run test:e2e
docker compose down -v
```

The tests use Chromium and the real Compose-served frontend/API at `http://127.0.0.1:8080`. PvP/PvAI and history persistence assertions call the real API. HTTP error responses and network failures are injected at the browser network boundary to verify recovery; those cases are not claimed as backend-generated faults. Playwright writes traces, screenshots and video on failure under `test-results/`.

CI workflow: `.github/workflows/frontend-e2e.yml`. It uses `npm ci`, starts Compose, waits for the same-origin proxied `/health` endpoint, runs Playwright, uploads evidence as a workflow artifact, and tears down the stack.

## History UI and API contract

The History page at `/history.html` requests the backend's confirmed `GET /api/history?limit=20&offset=0` endpoint. It renders the `GameHistoryResponse.items` envelope returned by the API, including mode, timestamps, status/result and move count. It never reads or writes game history in localStorage. Loading, empty, error and retry states are provided.

The browser test creates a real persisted game, confirms the new ID appears in `GET /api/history`, opens a fresh page, checks the history link, reloads the page and verifies the same persisted record remains visible. The persistence test is not skipped based on a 404 response.

Replay of individual moves is not implemented because no moves-detail/replay endpoint has been confirmed.

## Public deployment smoke

Not run in this change: M4 has not supplied a confirmed HTTPS release URL/release SHA. Do not treat localhost CI as public deployment evidence. Once M4 publishes a URL and release SHA, run the browser suite against the deployment and capture URL, browser/version, UTC timestamp, release SHA, screenshots/traces and result.

## Previous CI evidence (historical)

The earlier run on SHA `dcf6328a4a93f6c19ba3b6daf5c2a799c4b0dec0` had 12 passing tests and 1 skipped history-persistence test because it used the incorrect `/api/games/history` path. That result is historical and does not validate the updated history contract. The updated branch runs fresh E2E and full CI on the new HEAD; consult the PR's latest Actions checks for the current result.

Public HTTPS deployment smoke: **NOT RUN**; no verified public URL or deployed release SHA has been provided.

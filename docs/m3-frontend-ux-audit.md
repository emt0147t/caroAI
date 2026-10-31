# M3 frontend candidate — audit and validation record

## Validation target

- Candidate branch: `feature/m3-frontend-ux-polish`
- Pull request: #42
- Test stack: Docker Compose (PostgreSQL + FastAPI + Nginx), with Playwright/Chromium against the Nginx origin.
- Visual evidence: same 390 × 844 viewport for baseline (`develop` base SHA) and candidate (`after`); see the `playwright-evidence` Actions artifact.

## M3 status

| Item | Status | Evidence / remaining work |
|---|---|---|
| M3-01 Compose, Nginx root/proxy, API origin | Runtime path verified in CI | Baseline and candidate Compose stacks are started; Nginx proxy health is checked. Separate third-party API-origin/CORS deployment is not verified. |
| M3-02 Real History API, loading/empty/error/retry/persistence | Implemented and browser-tested | API error/retry, empty/malformed response, persisted entry, fresh page and reload are covered. |
| M3-03 Backend-authoritative state, busy lock, lost-response recovery | Implemented and browser-tested | PvP/PvAI API-driven moves, duplicate-submit lock, injected HTTP errors and lost-response GET recovery are covered. |
| M3-04 Win/draw and post-game lock | Implemented and browser-tested | Backend-authoritative X win and full-board draw states are rendered; all cells are disabled after completion. No separate results page is currently provided. |
| M3-05 Playwright flows and regression suite | Automated suite expanded | CI runs the browser suite against the Compose stack. Confirm the latest candidate run before marking this row green. |
| M3-06 Shared design tokens | Implemented across all screens | Shared semantic colors, typography, spacing, radii, shadows, focus and motion tokens are consumed by start, game and History screens. |
| M3-07 Start screen mode/difficulty/loading/error | Implemented | Real create-game POST, disabled/loading state, inline error and accessible mode/difficulty controls. |
| M3-08 Board contrast/turn/busy/responsive | Implemented and browser-tested | Contrast/status colors and busy lock are present; no horizontal overflow is tested at 320, 360, 390, 768 and 1280 px. |
| M3-09 History fields, empty state and reopen | Implemented and browser-tested | Date, mode, result and move count; empty/error/retry; opening a saved game restores backend state. Individual move-by-move replay is not available. |
| M3-10 Keyboard focus/reduced motion/responsive | Automated checks added | Visible focus ring and reduced-motion behavior are tested; manual screen-reader/assistive-technology testing remains recommended. |
| M3-11 Before/after evidence | Automated capture configured | CI captures start, game and History screenshots for base and candidate at the same 390 × 844 viewport and uploads them in `playwright-evidence`. |

## Remaining known limits

- Individual move replay is not exposed because the backend currently does not provide a stable move-detail/replay contract; the UI must not fabricate this history.
- A public HTTPS production smoke test requires the actual deployment URL and the release SHA from the deployment owner.
- The configurable `window.CAROAI_API_BASE_URL` hook exists, but a separately hosted cross-origin API is not part of the Compose same-origin acceptance test.
- Automated keyboard/focus checks do not replace a manual screen-reader and real-device review.

# M3 frontend candidate — audit and validation record

## Validation target

- Candidate branch: `feature/m3-frontend-ux-polish`
- Pull request: #42
- Test stack: Docker Compose (PostgreSQL + FastAPI + Nginx), with Playwright/Chromium against the Nginx origin.
- Visual evidence: same 390 × 844 viewport for baseline (`develop` base SHA) and candidate; see the `playwright-evidence` Actions artifact.

## M3 status

| Item | Status | Evidence / remaining work |
|---|---|---|
| M3-01 Compose, Nginx root/proxy, API origin | Runtime path verified in CI | Baseline and candidate Compose stacks start; Nginx proxy health is checked. The frontend supports a configurable API base URL. The backend does not currently configure CORS, so a genuinely cross-origin deployment still needs an explicit origin allowlist or same-origin reverse proxy. |
| M3-02 Real History API, loading/empty/error/retry/persistence | Implemented and browser-tested | API error/retry, empty/malformed response, persisted entry, fresh page and reload are covered. |
| M3-03 Backend-authoritative state, busy lock, lost-response recovery | Implemented and browser-tested | PvP/PvAI API-driven moves, duplicate-submit lock, injected HTTP errors and lost-response GET recovery are covered. |
| M3-04 Win/draw and post-game lock | Implemented and browser-tested | Backend-authoritative X win and full-board draw render a dedicated result card; all cells are disabled after completion. |
| M3-05 Playwright flows and regression suite | Passed on latest candidate run | 23 browser tests pass against the real Compose stack; see the latest `Frontend Browser E2E` run. |
| M3-06 Shared design tokens | Implemented across all screens | Shared semantic colors, typography, spacing, radii, shadows, focus and motion tokens are consumed by start, game and History screens. |
| M3-07 Start screen mode/difficulty/loading/error | Implemented and browser-tested | Real create-game POST, disabled/loading state, inline error, keyboard mode selection and selected difficulty are tested. |
| M3-08 Board contrast/turn/busy/responsive | Implemented and browser-tested | Busy state is exposed through `aria-busy`; no horizontal overflow is tested at 320, 360, 390, 768 and 1280 px. |
| M3-09 History fields, empty state and reopen | Implemented and browser-tested | Date, mode, result and move count; empty/error/retry; opening a saved game restores backend state. Individual move-by-move replay is not available. |
| M3-10 Keyboard focus/reduced motion/responsive | Automated checks passed | Visible focus ring and reduced-motion behavior are tested; manual screen-reader/assistive-technology testing remains recommended. |
| M3-11 Before/after evidence | Captured by CI | Start, game and History screenshots are captured from base and candidate at the same 390 × 844 viewport and uploaded in `playwright-evidence`. |

## Remaining known limits

- Individual move replay is not exposed because the backend currently does not provide a stable move-detail/replay contract; the UI must not fabricate this history.
- A public HTTPS production smoke test requires the actual deployment URL and the release SHA from the deployment owner.
- A separately hosted cross-origin API needs explicit CORS allowlisting. The same-origin Compose reverse-proxy path is the verified deployment mode.
- Automated keyboard/focus checks do not replace a manual screen-reader and real-device review.

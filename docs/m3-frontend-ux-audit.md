# M3 frontend candidate — audit and validation record

## Deployment / routing audit (M3-01)

Reviewed on `develop` at candidate base `138164803f3537d15ca90d9bc358f3f86528c4f3`.

- Docker Compose defines a `frontend` Nginx service, maps `FRONTEND_PORT` (default 8080) to port 80, mounts `./frontend/Caro_AI` read-only at `/usr/share/nginx/html`, and mounts `deploy/nginx-frontend.conf`.
- Nginx uses `/usr/share/nginx/html` as its root and `welcome.html` as the index.
- Nginx proxies `/api/` to `http://app:8000/api/` and `/health` to the backend health route.
- The browser pages use same-origin relative API URLs by default. They also read `window.CAROAI_API_BASE_URL` to support a separately configured API origin.
- Static config review completed. A live local Compose smoke test and a separately configured API-origin browser run still need CI/local execution; do not treat this document as evidence that those runtime checks passed.

## M3 status

| Item | Status | Evidence / remaining work |
|---|---|---|
| M3-01 Compose, root, proxy, configurable API origin | Config audit complete | Runtime local and external-origin smoke checks pending |
| M3-02 Real History API, loading/empty/error/retry/persistence | Implemented on `develop` | `tests/e2e/history.spec.cjs` checks API presence, persisted record, fresh page and reload |
| M3-03 Backend-authoritative state, busy lock, lost-response recovery | Implemented on `develop` | `tests/e2e/game.spec.cjs`; run CI on this candidate |
| M3-04 Win/draw and post-game lock | Implemented on `develop` | API-driven end-game and draw E2E coverage; dedicated result pages are not present in the current frontend |
| M3-05 Playwright PvP/PvAI/error/recovery/end-state/history | Tests present | CI run is required; do not mark green before run completion |
| M3-06 Shared design tokens | In progress | This PR adds shared accessibility/focus and reduced-motion tokens; colors/spacing remain page-specific |
| M3-07 Start screen mode/difficulty/loading/error | Implemented on `develop` | `welcome.html` uses backend create-game API |
| M3-08 Board contrast/turn/busy/responsive | Improved | Mobile board cell sizing adjusted for 360px; validate in browser CI |
| M3-09 History fields/empty state | Implemented on `develop` | Replay of individual moves is out of scope until backend provides a stable move-detail/replay API |
| M3-10 Keyboard focus/reduced motion/responsive | Improved | Shared visible focus ring, reduced-motion support and 360px viewport assertion added |
| M3-11 Before/after evidence | Pending | Capture screenshots on the same viewport and record the final CI candidate SHA after review |

## Known limits

- Individual move replay is not offered.
- Public HTTPS smoke test is not included; deployment URL and release SHA must be supplied by the deployment owner.
- The UX stylesheet does not replace browser/assistive-technology manual testing.

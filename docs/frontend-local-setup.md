# Running the CaroAI frontend with the backend

The supported local setup uses Nginx as a same-origin reverse proxy. The browser loads the UI and calls `/api` on the same origin; Nginx forwards API requests to FastAPI. This avoids cross-origin requests and does not require permissive CORS settings.

## Requirements

- Docker Desktop with Docker Compose v2
- Ports 8080, 8000 and 5432 available (or override them with environment variables)

## Start

From the repository root:

```powershell
docker compose up --build
```

Open **http://localhost:8080/**. The welcome page is served at that origin, and requests to `/api/*` are reverse-proxied to the backend container. To check the API through the same origin, open **http://localhost:8080/health**; a healthy response is JSON with `status: "ok"`.

Stop the stack with:

```powershell
docker compose down
```

The default API base URL remains empty intentionally: relative `/api` requests resolve to Nginx, not a separate frontend development server. Do not open the HTML file directly using `file://`.

## Frontend checks

Requires Node.js 20 or newer. No npm packages are needed:

```powershell
node --check frontend/Caro_AI/trong_tran/script.js
node --test tests/frontend-regression.test.cjs
docker compose config --quiet
```

The Node regression checks guard critical request contracts and state-handling paths in the lightweight frontend. They are source-level regression checks, not browser-driven end-to-end tests. The API/game rules remain backend-owned.

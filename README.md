# CaroAI — Gomoku 15×15 AI Gaming Platform

CaroAI is a full-stack 15 × 15 Gomoku (Cờ Caro) competitive gaming application featuring an authoritative FastAPI backend, a Python Minimax AI engine with alpha-beta pruning, a responsive modern web dashboard, persistent PostgreSQL storage, reproducible Docker containerization, and automated GitHub Actions CI/CD.

---

## 1. Project Overview
- **Repository**: [https://github.com/emt0147t/caroAI](https://github.com/emt0147t/caroAI)
- **Target Platform**: Render Web Service & Neon PostgreSQL
- **Public Bootstrap Demo URL**: [https://caroai-bootstrap-a9e753b33198.onrender.com](https://caroai-bootstrap-a9e753b33198.onrender.com) (Official main release URL pending promotion of PR #50)
- **Docker Hub Repository**: `docker.io/emt0147/caroai` (Bootstrap image: `docker.io/emt0147/caroai:bootstrap-a9e753b33198`)
- **Application Core**: 15 × 15 standard grid, zero client-side game logic authority, persistent game state, and move history.

---

## 2. Key Features
- **Human vs Human (PvP)**: Two players competing on the same device with alternating turns (X starts first).
- **Human vs AI (PvAI)**: Single-player mode against the intelligent CaroAI Minimax engine.
- **Three AI Difficulty Levels**:
  - `easy`: Basic heuristic evaluation for rapid casual play.
  - `medium`: Balanced positional scoring and threat detection.
  - `hard`: Deep Minimax search with alpha-beta pruning, tactical open-four / open-three pattern weighting.
- **Backend-Authoritative Rule Engine**: Turn transitions, move validation, 5-in-a-row victory detection, and 225-cell board draw calculations are 100% computed and verified by the backend.
- **Persistent Game History**: Real-time recording of games, moves, timestamps, and terminal results in PostgreSQL.
- **System Health & Readiness**: Separate `/health` (container liveness) and `/ready` (database connectivity probe) endpoints.
- **Modern Responsive Dashboard**: Interactive match center, real-time backend health pill, recent games preview widget, and 4-step game rules guide. Fully verified at 320px, 360px, 390px, 768px, and 1280px viewports.

---

## 3. Technology Stack
- **Backend**: Python 3.11, FastAPI, Uvicorn, SQLAlchemy 2.0, Psycopg2-binary, Pydantic v2.
- **AI Engine**: Python Minimax with Alpha-Beta Pruning and Gomoku heuristic evaluation.
- **Frontend**: Semantic HTML5, CSS3 with unified design tokens (`tokens.css`), Vanilla JavaScript (zero heavy framework dependencies).
- **Database**: PostgreSQL 15+, versioned SQL migrations tracked via `schema_migrations`.
- **Containerization**: Multi-stage Dockerfile (`python:3.11-slim`), non-root `appuser` (UID 10001), Docker Compose.
- **Reverse Proxy & Serving**: Unified FastAPI `StaticFiles` mounting for single-container cloud environments, optional Nginx reverse proxy for multi-container topologies.
- **CI/CD & Security**: GitHub Actions, Gitleaks secret scanning, Playwright E2E browser automation, pytest, flake8.

---

## 4. Architecture

```text
User Browser (Desktop / Mobile)
       |
       | HTTPS (TLS 1.3)
       v
Cloud Web Service (Render / Docker)
       |
       +---> Port ${PORT:-8000}
       |
       +---> Uvicorn ASGI Server
       |        |
       |        +---> FastAPI Application
       |                 |
       |                 +---> Static Frontend Mount (/, /history.html, /tokens.css, /trong_tran/*)
       |                 |
       |                 +---> REST API (/api/games, /api/history, /health, /ready)
       |                 |
       |                 +---> Minimax AI Engine (Alpha-Beta Pruning)
       |                 |
       |                 +---> SQLAlchemy Unit of Work & Repository
       |
       +---> PostgreSQL Production Database (Connection Pooling, Migrations, ACID Storage)
```

---

## 5. Repository Structure

```text
caroAI/
├── .github/workflows/      # CI/CD pipelines (ci-cd.yml, frontend-e2e.yml)
├── app/                    # Backend application source
│   ├── ai/                 # Minimax search engine and heuristic evaluators
│   ├── api/                # FastAPI routing (games, history, health, dependencies)
│   ├── db/                 # SQLAlchemy models, session management, and repository
│   ├── domain/             # Game rules, board representation, win/draw state
│   ├── schemas/            # Pydantic request/response validation schemas
│   └── services/           # GameService transactional orchestration
├── database/
│   └── migrations/         # Versioned SQL migration files (000, 001)
├── deploy/                 # Nginx proxy configuration
├── docs/                   # Architectural specs, QA matrices, and audit reports
│   └── final-project/      # Final project audits, conflict evidence, acceptance report
├── frontend/Caro_AI/       # Responsive frontend assets (welcome.html, history.html, trong_tran/)
├── scripts/                # Database migration and operational runner scripts
├── tests/                  # Pytest unit, API, postgres suites, and Playwright E2E specs
├── Dockerfile              # Multi-stage production container definition
├── docker-compose.yml      # Local development and multi-container Compose stack
└── requirements.txt        # Production dependency manifest
```

---

## 6. Local Setup (Without Docker)

### Prerequisites
- Python 3.11 installed (`python --version` -> `Python 3.11.x`)
- PostgreSQL 15+ running locally

### Installation Steps
```powershell
# 1. Clone repository and navigate to root
git clone https://github.com/emt0147t/caroAI.git
cd caroAI

# 2. Create and activate Python virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install production and development dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
```

---

## 7. Environment Variables

Create a `.env` file in the repository root (based on `.env.example`):

| Variable | Description | Local Default | Production Requirement |
|---|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://caroai_user:local_pass@localhost:5432/caroai_db` | Managed PostgreSQL URL (`postgres://...` auto-normalized) |
| `PORT` | Listening port for Uvicorn | `8000` | Injected dynamically by Render (e.g. `10000`) |
| `APP_ENV` | Application environment identifier | `development` | `production` |
| `CAROAI_API_BASE_URL` | Optional API origin for frontend | `""` (Same-origin default) | Omit / Leave empty for same-origin deployment |

---

## 8. Docker Setup (Single Container)

To build and run the production image independently:

```powershell
# Build image with candidate tag
docker build -t caroai:local .

# Run container with dynamic port and database URL
docker run -d `
  --name caroai-app `
  -p 8000:8000 `
  -e PORT=8000 `
  -e DATABASE_URL="postgresql://user:pass@host.docker.internal:5432/caroai_db" `
  caroai:local

# Inspect logs
docker logs -f caroai-app
```

---

## 9. Docker Compose Setup (Multi-Container Local Stack)

The recommended local development workflow uses Docker Compose:

```powershell
# 1. Configure environment file
Copy-Item .env.example .env

# 2. Build and launch services in background
docker compose up --build -d

# 3. Verify container statuses
docker compose ps

# 4. Check application health
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/ready
```

Access services:
- **Application Frontend**: `http://localhost:8080` (or `http://localhost:8000` via FastAPI mount)
- **API Swagger Documentation**: `http://localhost:8000/docs`
- **Database**: Port `5432` / `5433`

To stop containers while safely preserving database volumes:
```powershell
docker compose down
```
*(Do not pass `-v` unless you explicitly intend to delete local database data).*

---

## 10. PostgreSQL Setup
CaroAI uses standard PostgreSQL. In production or local setups:
1. Ensure the database user has rights to create tables and execute transactions.
2. The application handles connection URL forms `postgres://` and `postgresql://` by transparently normalizing them to `postgresql+psycopg2://`.
3. Connection pooling is enabled with `pool_pre_ping=True` to immediately recover from dropped cloud connections.

---

## 11. Database Migrations
Migrations are managed via explicit, versioned SQL files located in `database/migrations/`:
- `000_initial_schema.sql`: Base tables for `games`, `moves`, and `game_analysis`.
- `001_games_public_id.sql`: Generates and enforces unique `public_id` UUID strings for games.

Migrations are applied automatically on application startup via:
```powershell
python -m scripts.migrate_database
```
Execution is tracked in the `schema_migrations` table, ensuring idempotency and zero duplicate executions.

---

## 12. API Documentation

### Liveness & Readiness
- `GET /health`: Returns `{"status": "ok"}` when the ASGI application is alive.
- `GET /ready`: Returns `{"status": "ready", "database": "ok"}` when database `SELECT 1` succeeds; returns HTTP 503 if unavailable.

### Gameplay
- `POST /api/games`: Create a game. Body: `{"mode": "HUMAN_VS_HUMAN"}` or `{"mode": "HUMAN_VS_AI"}`. Returns HTTP 201 with `id` and initial board.
- `GET /api/games/{game_id}`: Returns authoritative game state, board matrix, move count, and status.
- `POST /api/games/{game_id}/moves`: Submit a human move. Body: `{"row": 7, "col": 7}`. Returns HTTP 200 with updated game state.
- `POST /api/games/{game_id}/ai-move`: Trigger an AI response. Body: `{"difficulty": "hard"}`. Returns HTTP 200 with AI move coordinates and new game state.

### History
- `GET /api/history?limit=20&offset=0`: Retrieves paginated list of completed and in-progress games from PostgreSQL.

Interactive OpenAPI UI is available at `/docs`.

---

## 13. Testing Commands

### Python Unit & API Tests
```powershell
py -3.11 -m pytest -q tests/
```

### PostgreSQL Acceptance & Rollback Test
```powershell
$env:TEST_DATABASE_URL = "postgresql+psycopg2://caroai_test:caroai_test_password@localhost:5432/caroai_test"
$env:CAROAI_TEST_DATABASE_CONFIRMED = "disposable-test-database"
$env:CAROAI_TEST_POSTGRES_ALLOWLIST = "localhost:5432/caroai_test"
py -3.11 -m pytest -q tests/test_database_postgres.py tests/postgres_suite.py
```

### Code Style & Linting
```powershell
py -3.11 -m flake8 app tests scripts --count --max-complexity=10 --max-line-length=127 --statistics
```

### Frontend Syntax & Regression Tests
```powershell
node --check frontend/Caro_AI/trong_tran/script.js
node --test tests/frontend-regression.test.cjs
```

### Playwright Browser E2E Suite
```powershell
npm run test:e2e
```

---

## 14. CI/CD Pipeline
GitHub Actions pipeline (`.github/workflows/ci-cd.yml`) automates verification on pushes and PRs:
1. **Frontend Job**: Syntax validation and regression checks.
2. **Python Test Job**: Flake8 linting, pytest unit suites, docker compose config validation.
3. **PostgreSQL Integration Job**: Spawns ephemeral PostgreSQL 15 service, verifies schema migrations, transactional atomicity, and rollback integrity.
4. **Compose Smoke Job**: Boots full Compose stack, executes PvP/PvAI move sequences, restarts container, and verifies game state persistence.
5. **Secret Scan Job**: Gitleaks PR check and full repository history audit.
6. **Candidate Build Job**: Multi-stage build producing SHA-tagged image candidate without registry push.
7. **Production Release Job**: Triggered manually via `workflow_dispatch` on `main` when approved. Publishes traceable commit-SHA-tagged images (tracked by image content digest) to Docker Hub, calls the Render Deploy Hook, and verifies live public HTTPS endpoints. Note: Promotion from `develop` to `main` requires a Pull Request with at least 1 approval (branch protection on `main`), followed by dispatching this workflow on `main`.

---

## 15. Docker Hub Image Reference
- **Docker Hub Account**: `emt0147`
- **Repository**: `docker.io/emt0147/caroai`
- **Bootstrap Image (Live Demo)**:
  - **Tag**: `docker.io/emt0147/caroai:bootstrap-a9e753b33198`
  - **Status**: **VERIFIED / PUBLISHED** (Manually published and running in the bootstrap Web Service)
  - **Pull command**:
    ```bash
    docker pull emt0147/caroai:bootstrap-a9e753b33198
    ```
- **Automated Production Release**:
  - **Status**: **PENDING / NOT RUN** (Automated release workflow on protected `main` has not run; full-SHA and short-SHA release tags generated by GitHub Actions remain pending)
  - **Tags & Digest**:
    - Full Commit SHA: `docker.io/emt0147/caroai:<commit-sha>`
    - Short SHA: `docker.io/emt0147/caroai:<short-sha>`
    - Digest Tracking: Cryptographic image digest captured in CI release job via `$IMAGE_DIGEST`

---

## 16. Deployment Instructions (Render Web Service & Neon PostgreSQL)

### 16.1 Neon Database Setup
1. Create a project in [Neon Console](https://neon.tech) (e.g. `caroai-demo`, AWS Singapore `ap-southeast-1`, PostgreSQL 18, database `neondb`, branch `production`).
2. Copy the **direct (non-pooler)** PostgreSQL connection string.
   - **Connection Mode**: The deployed CaroAI production service uses Neon's direct connection rather than the pooled connection (`-pooler` endpoint on port 5432/6543).
   - **Internal Pooling Distinction**: CaroAI's FastAPI application manages its own internal connection pooling via SQLAlchemy (`pool_pre_ping=True`, pool recycling), so it connects directly to Neon without an external transaction pooler.
   - **TLS & Channel Binding**: The deployed connection string requires TLS (`sslmode=require`) and channel binding (`channel_binding=require`).
   - **Security Policy**: Never print, commit, or document the actual hostname, username, password, or `DATABASE_URL` in documentation or source code.

### 16.2 Render Web Service Setup
1. **Create Web Service**:
   - Choose **Deploy an existing image from a registry**.
   - Image URL: `docker.io/emt0147/caroai:bootstrap-a9e753b33198` (or the automated release tag `docker.io/emt0147/caroai:<sha>`).
   - Instance Type: **Free**.
2. **Environment Variables**:
   - `DATABASE_URL`: Connection string from your Neon PostgreSQL instance (configured in Render environment settings).
   - `APP_ENV`: `production`
   - `PORT`: Automatically assigned by Render (e.g. `10000`).
3. **Health Check Path**:
   - Set to `/ready` (validates both container liveness and database `SELECT 1` connectivity).
4. **Deploy & Verification**:
   - Save changes. Render pulls the image, runs migrations on startup (`000_initial_schema`, `001_games_public_id`), and exposes the public HTTPS URL.

---

## 17. Public HTTPS Application URL
- **Bootstrap / Demo Service**: **LIVE & VERIFIED**
  - **Public URL**: [https://caroai-bootstrap-a9e753b33198.onrender.com](https://caroai-bootstrap-a9e753b33198.onrender.com)
  - **Render Service ID**: `srv-dbkd2dflk1mc73fd2ukg`
  - **Bootstrap Image**: `emt0147/caroai:bootstrap-a9e753b33198`
  - **Instance Type**: Free
  - **Health Path**: `/ready`
  - **Verified Endpoints**: `/health` (200 OK), `/ready` (200 OK), `/` (200 OK), `/history.html` (200 OK), `/api/history` (200 OK), `/tokens.css` (200 OK).
- **Official Production Release**: **PENDING / NOT RUN**
  - The automated release workflow on protected `main` has not run.
  - Full-SHA and short-SHA release tags from GitHub Actions are still pending.
  - **Environment Variable `CAROAI_PUBLIC_URL`**: Status is **UNCONFIRMED — PENDING OWNER VERIFICATION** under GitHub Settings → Environments → `production`. Do not claim it is configured or infer its presence from the five Environment secrets.
  - Illustrative Endpoint Format: `https://<service-name>.onrender.com`

---

## 18. Production PostgreSQL Configuration Overview (Neon PostgreSQL)
- **Database Provider**: Neon Serverless PostgreSQL
- **Project**: `caroai-demo`
- **Region**: AWS Singapore (`ap-southeast-1`)
- **Plan**: Free
- **PostgreSQL Version**: 18
- **Database Name**: `neondb`
- **Branch**: `production`
- **Configuration**: `DATABASE_URL` is configured in Render Web Service environment settings using Neon direct (non-pooler) connection with `sslmode=require` and `channel_binding=require` (actual hostname, username, password, and connection string are never written into documentation).
- **Driver**: Psycopg2-binary with SQLAlchemy internal connection pooling (`pool_pre_ping=True`).
- **Migrations**: `000_initial_schema.sql` and `001_games_public_id.sql` applied successfully on startup; Render startup logs confirmed schema up to date.
- **Persistence Verification**: **PASS**.
  - Verified on live cloud infrastructure via Render Web Service restart.
  - Interactive PvP and PvAI matches created and verified; AI engine move returned player O.
  - Full game details and histories retrievable from Neon PostgreSQL via `/api/history`.
  - Both PvP and PvAI games remained fully accessible after Render Web Service restart (`POST-RESTART PERSISTENCE: PASS`).
- **Fail-Safe**: Zero client-side state is trusted; database is the single source of truth.

---

## 19. Troubleshooting

| Symptom | Cause | Solution |
|---|---|---|
| Container exits with code 1 | Missing or invalid `DATABASE_URL` | Ensure `DATABASE_URL` is set and PostgreSQL is reachable. |
| Container fails health check on Render | Port mismatch | Verify `Dockerfile` uses `${PORT:-8000}`. |
| `ModuleNotFoundError: sqlalchemy` locally | Wrong Python environment | Use Python 3.11 with dependencies installed from `requirements.txt`. |
| 503 Service Unavailable on move | Database connection dropped | Verify PostgreSQL service status; check `/ready` endpoint. |
| CORS errors in browser | Calling cross-origin API | Serve frontend and API from same origin (default container setup). |

---

## 20. Demonstration Instructions

### 20.1 Local Environment Demonstration
1. Start the application locally using Docker Compose:
   ```powershell
   docker compose up --build -d
   ```
   *(Or run locally with Python: `uvicorn app.main:app --host 0.0.0.0 --port 8000`).*
2. Open the web interface in your browser at `http://localhost:8000` (or `http://localhost:8080` if accessing via Nginx).
3. Observe the green **Hệ thống sẵn sàng** status pill in the top navigation bar (verifying backend liveness and database readiness).
4. Select **Người vs AI**, choose difficulty **Khó (Minimax)**, and click **Bắt đầu ván đấu →**.
5. Play alternating moves on the 15 × 15 board; observe real-time AI responses calculated server-side by the Minimax engine.
6. Complete a game with a 5-in-a-row alignment; observe the backend-authoritative victory dialog and win state.
7. Click **Lịch sử** in the top navigation bar; verify the finished game appears in the list with move count, duration, and result.
8. Click **Mở bàn cờ →**; verify the full board and move sequence reload exactly from PostgreSQL persistence.

### 20.2 Online Demonstration (Live Cloud Bootstrap Service)
The live bootstrap deployment is available for online evaluation:
- **Live Demo URL**: [https://caroai-bootstrap-a9e753b33198.onrender.com](https://caroai-bootstrap-a9e753b33198.onrender.com)
- **Evaluation Steps**:
  1. Open [https://caroai-bootstrap-a9e753b33198.onrender.com](https://caroai-bootstrap-a9e753b33198.onrender.com) in your web browser.
  2. Confirm the green **Hệ thống sẵn sàng** status pill in the top navigation bar (verifying backend `/health` and Neon PostgreSQL `/ready`).
  3. Play **Người vs Người (PvP)**: Click **Người vs Người**, take alternating moves on the 15 × 15 grid, verify coordinates, turn transitions, and 5-in-a-row victory detection.
  4. Play **Người vs AI (PvAI)**: Click **Người vs AI**, select difficulty, and make your move; observe server-side Minimax calculation returning player O moves.
  5. Check Match History: Click **Lịch sử** (`/history.html`) to view persisted matches from Neon PostgreSQL; click **Mở bàn cờ →** to reload exact move history.
  6. Persistence Verification: Cloud database persistence has been verified across Render Web Service restarts (`POST-RESTART PERSISTENCE: PASS`).
- **Official Production Release Note**: The official automated release workflow from protected `main` remains pending promotion of PR #50 and manual dispatch.

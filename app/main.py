from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes_health import router as health_router
from app.api.routes_games import router as games_router
from app.api.routes_history import router as history_router
from app.api.routes_qa import router as qa_router


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "Caro_AI"

app = FastAPI(
    title="CaroAI API",
    version="0.1.0",
    description="Backend API and static frontend for CaroAI",
)

app.include_router(health_router)
app.include_router(games_router)
app.include_router(history_router)
app.include_router(qa_router)


@app.get("/", include_in_schema=False)
def root() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "welcome.html")


# The production Docker image contains both the API and the static frontend.
# Keep this mount after API routes so /api, /health, and /ready retain priority.
app.mount(
    "/",
    StaticFiles(directory=FRONTEND_DIR, html=True),
    name="frontend",
)

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.qa_security import load_qa_config
from app.api.routes_games import router as games_router
from app.api.routes_health import router as health_router
from app.api.routes_history import router as history_router
from app.api.routes_qa import router as qa_router
from app.observability import install_observability


FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend" / "Caro_AI"


def create_app() -> FastAPI:
    """Build API and keep QA routes fail-closed without complete opt-in."""
    application = FastAPI(
        title="CaroAI API",
        version="0.1.0",
        description="Backend API and static frontend for CaroAI",
    )
    application.include_router(health_router)
    application.include_router(games_router)
    application.include_router(history_router)

    qa_config = load_qa_config()
    application.state.qa_config = qa_config
    application.include_router(qa_router)

    install_observability(application)

    @application.get("/", include_in_schema=False)
    def root() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "welcome.html")

    # Keep this mount after API routes so /api, /health, and /ready retain priority.
    application.mount(
        "/",
        StaticFiles(directory=FRONTEND_DIR, html=True),
        name="frontend",
    )
    return application


app = create_app()

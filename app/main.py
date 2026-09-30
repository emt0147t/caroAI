from fastapi import FastAPI

from app.api.routes_health import router as health_router
from app.api.routes_games import router as games_router


app = FastAPI(
    title="CaroAI API",
    version="0.1.0",
    description="Backend API for CaroAI",
)

app.include_router(health_router)
app.include_router(games_router)


@app.get("/")
def root():
    return {
        "message": "CaroAI API is running",
        "version": "0.1.0",
    }
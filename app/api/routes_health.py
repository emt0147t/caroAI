from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.db.database import get_engine

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    """Application liveness; deliberately independent of database availability."""
    return {"status": "ok"}


@router.get("/ready")
def readiness_check():
    """Report ready only when the configured database accepts a query."""
    try:
        with get_engine().connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:
        raise HTTPException(
            status_code=503,
            detail="Database is not ready",
        ) from exc
    return {"status": "ready", "database": "ok"}

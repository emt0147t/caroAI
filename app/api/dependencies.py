"""FastAPI dependencies for request-scoped application services."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.repository import SQLAlchemyGameRepository
from app.services.game_service import GameService


def get_game_service(db: Session = Depends(get_db)) -> GameService:
    """Provide a GameService backed by the PostgreSQL request session."""
    return GameService(SQLAlchemyGameRepository(db))

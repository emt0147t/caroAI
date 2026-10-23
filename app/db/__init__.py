"""Database foundation for CaroAI.

Business models and repositories remain intentionally unimplemented until
their contracts are confirmed.
"""

from .database import SessionLocal, get_db, get_engine
from .models import Base

__all__ = ["Base", "SessionLocal", "get_db", "get_engine"]

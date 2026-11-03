"""SQLAlchemy models for CaroAI persistence."""
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    CHAR,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class Game(Base):
    """A persisted Caro game.

    `id` is the internal database key. `public_id` preserves the existing
    UUID-shaped API identifier and is the value exposed to clients.
    """

    __tablename__ = "games"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
    )
    public_id = Column(
        String(36),
        nullable=False,
        unique=True,
        index=True,
        default=lambda: str(uuid4()),
    )
    mode = Column(String(32), nullable=False)
    difficulty = Column(String(16), nullable=True)
    status = Column(
        String(16), nullable=False, server_default=text("'IN_PROGRESS'")
    )
    # result is NULL while in progress; terminal values are X_WON, O_WON, or DRAW.
    result = Column(String(16), nullable=True)
    started_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    ended_at = Column(DateTime(timezone=True), nullable=True)

    moves = relationship("Move", back_populates="game")
    analyses = relationship("GameAnalysis", back_populates="game")

    # TODO(M1): Confirm enum enforcement strategy and allowed mode/status values.
    # TODO(M1/M4): Migrate existing rows to populated public_id values before
    # making this column required in any already-provisioned database.


class Move(Base):
    """A move belonging to one game."""

    __tablename__ = "moves"
    __table_args__ = (
        CheckConstraint("row >= 0 AND row <= 14", name="ck_moves_row_on_board"),
        CheckConstraint("col >= 0 AND col <= 14", name="ck_moves_col_on_board"),
        CheckConstraint("player IN ('X', 'O')", name="ck_moves_player_x_or_o"),
        CheckConstraint("move_number > 0", name="ck_moves_move_number_positive"),
        UniqueConstraint("game_id", "move_number", name="uq_moves_game_move_number"),
    )

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
    )
    game_id = Column(BigInteger, ForeignKey("games.id"), nullable=False)
    player = Column(CHAR(1), nullable=False)
    row = Column(SmallInteger, nullable=False)
    col = Column(SmallInteger, nullable=False)
    move_number = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    game = relationship("Game", back_populates="moves")


class GameAnalysis(Base):
    """Analysis data belonging to a game, optionally associated with a move."""

    __tablename__ = "game_analysis"
    __table_args__ = (
        CheckConstraint(
            "best_move_row IS NULL OR (best_move_row >= 0 AND best_move_row <= 14)",
            name="ck_game_analysis_best_move_row_on_board",
        ),
        CheckConstraint(
            "best_move_col IS NULL OR (best_move_col >= 0 AND best_move_col <= 14)",
            name="ck_game_analysis_best_move_col_on_board",
        ),
    )

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        Identity(always=True),
        primary_key=True,
    )
    game_id = Column(BigInteger, ForeignKey("games.id"), nullable=False, index=True)
    move_id = Column(BigInteger, ForeignKey("moves.id"), nullable=True)
    score = Column(DOUBLE_PRECISION, nullable=True)
    best_move_row = Column(SmallInteger, nullable=True)
    best_move_col = Column(SmallInteger, nullable=True)
    classification = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)

    game = relationship("Game", back_populates="analyses")

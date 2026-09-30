"""SQLAlchemy models for the confirmed portions of the Sprint 1 design.

Open contract decisions are deliberately not encoded here. See
docs/database-design.md and the TODO comments below before tightening the
schema.
"""

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
    """A persisted Caro game."""

    __tablename__ = "games"

    id = Column(BigInteger, Identity(always=True), primary_key=True)
    mode = Column(String(32), nullable=False)
    difficulty = Column(String(16), nullable=True)
    status = Column(
        String(16), nullable=False, server_default=text("'IN_PROGRESS'")
    )
    result = Column(String(16), nullable=True)
    started_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    ended_at = Column(DateTime(timezone=True), nullable=True)

    moves = relationship("Move", back_populates="game")
    analyses = relationship("GameAnalysis", back_populates="game")

    # TODO(M1): Confirm enum enforcement strategy (PostgreSQL ENUM vs CHECK)
    # and the complete allowed values before adding database constraints.
    # TODO(M1): Confirm status/result consistency and transition semantics.
    # TODO(M1): Confirm whether difficulty nullability depends on mode.
    # TODO(M1/Team): Confirm BIGINT identity against the application/API ID contract.


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

    id = Column(BigInteger, Identity(always=True), primary_key=True)
    game_id = Column(BigInteger, ForeignKey("games.id"), nullable=False)
    player = Column(CHAR(1), nullable=False)
    row = Column(SmallInteger, nullable=False)
    col = Column(SmallInteger, nullable=False)
    move_number = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    game = relationship("Game", back_populates="moves")

    # TODO(M1): Confirm whether UNIQUE (game_id, row, col) is compatible with
    # undo/replay behavior before adding it.
    # TODO(M1/Team): Confirm delete behavior; no database or ORM cascade is set.


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

    id = Column(BigInteger, Identity(always=True), primary_key=True)
    game_id = Column(BigInteger, ForeignKey("games.id"), nullable=False, index=True)
    move_id = Column(BigInteger, ForeignKey("moves.id"), nullable=True)
    score = Column(DOUBLE_PRECISION, nullable=True)
    best_move_row = Column(SmallInteger, nullable=True)
    best_move_col = Column(SmallInteger, nullable=True)
    classification = Column(Text, nullable=True)
    explanation = Column(Text, nullable=True)

    game = relationship("Game", back_populates="analyses")

    # TODO(M1/Team): Confirm whether move_id needs a composite FK with game_id.
    # TODO(M1/Team): Confirm analysis cardinality; intentionally no UNIQUE on
    # move_id and no ORM relationship to Move are defined.
    # TODO(M1): Confirm score/classification types and any allowed value ranges.


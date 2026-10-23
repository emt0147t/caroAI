-- Versioned baseline for a fresh PostgreSQL database.
-- IF NOT EXISTS also makes this safe to run against a legacy schema: existing
-- tables are not altered here, and later migrations handle schema changes.
CREATE TABLE IF NOT EXISTS games (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    public_id VARCHAR(36) NOT NULL UNIQUE,
    mode VARCHAR(32) NOT NULL,
    difficulty VARCHAR(16),
    status VARCHAR(16) NOT NULL DEFAULT 'IN_PROGRESS',
    result VARCHAR(16),
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS moves (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    game_id BIGINT NOT NULL REFERENCES games(id),
    player CHAR(1) NOT NULL,
    "row" SMALLINT NOT NULL,
    "col" SMALLINT NOT NULL,
    move_number INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ck_moves_row_on_board CHECK ("row" >= 0 AND "row" <= 14),
    CONSTRAINT ck_moves_col_on_board CHECK ("col" >= 0 AND "col" <= 14),
    CONSTRAINT ck_moves_player_x_or_o CHECK (player IN ('X', 'O')),
    CONSTRAINT ck_moves_move_number_positive CHECK (move_number > 0),
    CONSTRAINT uq_moves_game_move_number UNIQUE (game_id, move_number)
);

CREATE TABLE IF NOT EXISTS game_analysis (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    game_id BIGINT NOT NULL REFERENCES games(id),
    move_id BIGINT REFERENCES moves(id),
    score DOUBLE PRECISION,
    best_move_row SMALLINT,
    best_move_col SMALLINT,
    classification TEXT,
    explanation TEXT,
    CONSTRAINT ck_game_analysis_best_move_row_on_board
        CHECK (best_move_row IS NULL OR (best_move_row >= 0 AND best_move_row <= 14)),
    CONSTRAINT ck_game_analysis_best_move_col_on_board
        CHECK (best_move_col IS NULL OR (best_move_col >= 0 AND best_move_col <= 14))
);
CREATE INDEX IF NOT EXISTS ix_game_analysis_game_id ON game_analysis (game_id);

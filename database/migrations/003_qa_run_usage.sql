-- Retain QA game-creation usage until the signed capability expires.
-- Cleanup removes QA game data but must not reset the per-run creation quota.
CREATE TABLE IF NOT EXISTS qa_run_usage (
    qa_run_id VARCHAR(32) PRIMARY KEY,
    games_created INTEGER NOT NULL CHECK (games_created >= 0),
    expires_at BIGINT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_qa_run_usage_expires_at ON qa_run_usage (expires_at);

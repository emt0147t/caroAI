-- Add a nullable, run-scoped tag for controlled production acceptance games.
-- Ordinary games keep NULL and can never be selected by a QA cleanup request.
ALTER TABLE games ADD COLUMN IF NOT EXISTS qa_run_id VARCHAR(32);
CREATE INDEX IF NOT EXISTS ix_games_qa_run_id ON games (qa_run_id);

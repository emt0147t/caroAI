-- Add public IDs without changing the internal BIGINT primary key.
-- PostgreSQL 13+ provides gen_random_uuid() in core.
ALTER TABLE games ADD COLUMN IF NOT EXISTS public_id VARCHAR(36);
UPDATE games SET public_id = gen_random_uuid()::text WHERE public_id IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS ix_games_public_id ON games (public_id);
ALTER TABLE games ALTER COLUMN public_id SET NOT NULL;

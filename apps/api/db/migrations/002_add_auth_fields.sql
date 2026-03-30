BEGIN;

ALTER TABLE users
  ADD COLUMN password_hash TEXT,
  ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT TRUE,
  ADD COLUMN is_verified BOOLEAN NOT NULL DEFAULT FALSE;

UPDATE users
SET password_hash = COALESCE(password_hash, ''),
    is_active = COALESCE(is_active, TRUE),
    is_verified = COALESCE(is_verified, FALSE);

ALTER TABLE users
  ALTER COLUMN password_hash SET NOT NULL;

CREATE INDEX idx_users_is_active ON users(is_active);
CREATE INDEX idx_users_is_verified ON users(is_verified);

COMMIT;

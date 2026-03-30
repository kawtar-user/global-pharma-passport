BEGIN;

DROP INDEX IF EXISTS idx_users_is_verified;
DROP INDEX IF EXISTS idx_users_is_active;

ALTER TABLE users
  DROP COLUMN IF EXISTS is_verified,
  DROP COLUMN IF EXISTS is_active,
  DROP COLUMN IF EXISTS password_hash;

COMMIT;

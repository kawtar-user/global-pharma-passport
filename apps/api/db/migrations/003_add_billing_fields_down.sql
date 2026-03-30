BEGIN;

DROP INDEX IF EXISTS idx_subscriptions_user_status;
DROP INDEX IF EXISTS idx_users_stripe_customer_id;

ALTER TABLE subscriptions
  DROP COLUMN IF EXISTS trial_ends_at,
  DROP COLUMN IF EXISTS provider_price_id;

ALTER TABLE users
  DROP COLUMN IF EXISTS stripe_customer_id;

COMMIT;

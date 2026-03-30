BEGIN;

ALTER TABLE users
  ADD COLUMN stripe_customer_id TEXT UNIQUE;

ALTER TABLE subscriptions
  ADD COLUMN provider_price_id TEXT,
  ADD COLUMN trial_ends_at TIMESTAMPTZ;

CREATE INDEX idx_users_stripe_customer_id ON users(stripe_customer_id);
CREATE INDEX idx_subscriptions_user_status ON subscriptions(user_id, status);

COMMIT;

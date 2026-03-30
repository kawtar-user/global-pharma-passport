BEGIN;

CREATE TABLE product_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,
  session_id TEXT,
  event_name TEXT NOT NULL,
  locale VARCHAR(10),
  country_code CHAR(2),
  plan_code TEXT,
  source TEXT,
  properties JSONB NOT NULL DEFAULT '{}'::JSONB,
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT product_events_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT product_events_country_fk FOREIGN KEY (country_code) REFERENCES countries(code),
  CONSTRAINT product_events_properties_chk CHECK (jsonb_typeof(properties) = 'object')
);

CREATE INDEX idx_product_events_user_id ON product_events(user_id);
CREATE INDEX idx_product_events_event_name ON product_events(event_name);
CREATE INDEX idx_product_events_occurred_at ON product_events(occurred_at DESC);
CREATE INDEX idx_product_events_plan_code ON product_events(plan_code);
CREATE INDEX idx_product_events_properties_gin ON product_events USING GIN (properties);

COMMIT;

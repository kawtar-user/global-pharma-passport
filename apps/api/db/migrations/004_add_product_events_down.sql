BEGIN;

DROP INDEX IF EXISTS idx_product_events_properties_gin;
DROP INDEX IF EXISTS idx_product_events_plan_code;
DROP INDEX IF EXISTS idx_product_events_occurred_at;
DROP INDEX IF EXISTS idx_product_events_event_name;
DROP INDEX IF EXISTS idx_product_events_user_id;

DROP TABLE IF EXISTS product_events;

COMMIT;

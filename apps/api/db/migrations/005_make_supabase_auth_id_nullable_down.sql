UPDATE users
SET supabase_auth_id = gen_random_uuid()
WHERE supabase_auth_id IS NULL;

ALTER TABLE users
ALTER COLUMN supabase_auth_id SET NOT NULL;

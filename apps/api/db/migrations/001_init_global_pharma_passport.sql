BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TYPE user_role AS ENUM ('patient', 'pharmacist', 'admin');
CREATE TYPE medication_source AS ENUM ('manual', 'prescription_scan', 'import', 'api');
CREATE TYPE medication_status AS ENUM ('active', 'paused', 'stopped');
CREATE TYPE equivalence_type AS ENUM ('same_active_ingredient', 'same_combo', 'therapeutic_alternative');
CREATE TYPE risk_level AS ENUM ('minor', 'moderate', 'major', 'contraindicated');
CREATE TYPE prescription_processing_status AS ENUM ('uploaded', 'processing', 'processed', 'failed');
CREATE TYPE passport_status AS ENUM ('draft', 'active', 'revoked', 'expired');
CREATE TYPE subscription_status AS ENUM ('trialing', 'active', 'past_due', 'canceled', 'expired');
CREATE TYPE api_client_status AS ENUM ('active', 'disabled');

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

CREATE TABLE countries (
  code CHAR(2) PRIMARY KEY,
  name TEXT NOT NULL,
  phone_code TEXT,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE supported_languages (
  code VARCHAR(10) PRIMARY KEY,
  name TEXT NOT NULL,
  is_rtl BOOLEAN NOT NULL DEFAULT FALSE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  supabase_auth_id UUID NOT NULL UNIQUE,
  email CITEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  preferred_language VARCHAR(10) NOT NULL DEFAULT 'fr',
  country_code CHAR(2),
  role user_role NOT NULL DEFAULT 'patient',
  accepted_terms_at TIMESTAMPTZ,
  last_login_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT users_email_format_chk CHECK (POSITION('@' IN email::TEXT) > 1),
  CONSTRAINT users_full_name_chk CHECK (LENGTH(BTRIM(full_name)) >= 2),
  CONSTRAINT users_language_fk FOREIGN KEY (preferred_language) REFERENCES supported_languages(code),
  CONSTRAINT users_country_fk FOREIGN KEY (country_code) REFERENCES countries(code)
);

CREATE TABLE user_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE,
  date_of_birth DATE,
  sex TEXT,
  weight_kg NUMERIC(5,2),
  height_cm NUMERIC(5,2),
  blood_type TEXT,
  chronic_conditions_text TEXT,
  allergies_text TEXT,
  emergency_contact_name TEXT,
  emergency_contact_phone TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT user_profiles_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT user_profiles_weight_chk CHECK (weight_kg IS NULL OR weight_kg > 0),
  CONSTRAINT user_profiles_height_chk CHECK (height_cm IS NULL OR height_cm > 0)
);

CREATE TABLE clinical_conditions (
  code TEXT PRIMARY KEY,
  system_name TEXT NOT NULL,
  display_name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE user_conditions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  condition_code TEXT NOT NULL,
  diagnosed_at DATE,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT user_conditions_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT user_conditions_condition_fk FOREIGN KEY (condition_code) REFERENCES clinical_conditions(code),
  CONSTRAINT user_conditions_unique UNIQUE (user_id, condition_code)
);

CREATE TABLE active_ingredients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  inn_name TEXT NOT NULL,
  atc_code TEXT,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT active_ingredients_inn_name_chk CHECK (LENGTH(BTRIM(inn_name)) >= 2)
);

CREATE TABLE dosage_forms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  route TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT dosage_forms_code_chk CHECK (LENGTH(BTRIM(code)) >= 2)
);

CREATE TABLE drug_products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  brand_name TEXT NOT NULL,
  country_code CHAR(2) NOT NULL,
  manufacturer TEXT,
  marketing_authorization_holder TEXT,
  marketing_status TEXT NOT NULL DEFAULT 'active',
  local_license_number TEXT,
  description TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT drug_products_country_fk FOREIGN KEY (country_code) REFERENCES countries(code),
  CONSTRAINT drug_products_brand_name_chk CHECK (LENGTH(BTRIM(brand_name)) >= 2)
);

CREATE TABLE drug_presentations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  drug_product_id UUID NOT NULL,
  dosage_form_id UUID NOT NULL,
  route TEXT,
  strength_text TEXT NOT NULL,
  package_description TEXT,
  pack_size INTEGER,
  rx_required BOOLEAN NOT NULL DEFAULT TRUE,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT drug_presentations_product_fk FOREIGN KEY (drug_product_id) REFERENCES drug_products(id) ON DELETE CASCADE,
  CONSTRAINT drug_presentations_dosage_form_fk FOREIGN KEY (dosage_form_id) REFERENCES dosage_forms(id),
  CONSTRAINT drug_presentations_strength_chk CHECK (LENGTH(BTRIM(strength_text)) >= 1),
  CONSTRAINT drug_presentations_pack_size_chk CHECK (pack_size IS NULL OR pack_size > 0)
);

CREATE TABLE drug_presentation_ingredients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  drug_presentation_id UUID NOT NULL,
  active_ingredient_id UUID NOT NULL,
  strength_value NUMERIC(12,4),
  strength_unit TEXT,
  is_primary BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT drug_presentation_ingredients_presentation_fk FOREIGN KEY (drug_presentation_id) REFERENCES drug_presentations(id) ON DELETE CASCADE,
  CONSTRAINT drug_presentation_ingredients_ingredient_fk FOREIGN KEY (active_ingredient_id) REFERENCES active_ingredients(id),
  CONSTRAINT drug_presentation_ingredients_strength_chk CHECK (strength_value IS NULL OR strength_value > 0),
  CONSTRAINT drug_presentation_ingredients_unique UNIQUE (drug_presentation_id, active_ingredient_id)
);

CREATE TABLE drug_synonyms (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  active_ingredient_id UUID,
  drug_product_id UUID,
  synonym TEXT NOT NULL,
  language_code VARCHAR(10),
  country_code CHAR(2),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT drug_synonyms_ingredient_fk FOREIGN KEY (active_ingredient_id) REFERENCES active_ingredients(id) ON DELETE CASCADE,
  CONSTRAINT drug_synonyms_product_fk FOREIGN KEY (drug_product_id) REFERENCES drug_products(id) ON DELETE CASCADE,
  CONSTRAINT drug_synonyms_language_fk FOREIGN KEY (language_code) REFERENCES supported_languages(code),
  CONSTRAINT drug_synonyms_country_fk FOREIGN KEY (country_code) REFERENCES countries(code),
  CONSTRAINT drug_synonyms_owner_chk CHECK (
    (active_ingredient_id IS NOT NULL AND drug_product_id IS NULL)
    OR (active_ingredient_id IS NULL AND drug_product_id IS NOT NULL)
  )
);

CREATE TABLE drug_equivalents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_drug_presentation_id UUID NOT NULL,
  target_drug_presentation_id UUID NOT NULL,
  equivalence_type equivalence_type NOT NULL,
  equivalence_score NUMERIC(5,2) NOT NULL,
  clinical_notes TEXT,
  is_bidirectional BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT drug_equivalents_source_fk FOREIGN KEY (source_drug_presentation_id) REFERENCES drug_presentations(id) ON DELETE CASCADE,
  CONSTRAINT drug_equivalents_target_fk FOREIGN KEY (target_drug_presentation_id) REFERENCES drug_presentations(id) ON DELETE CASCADE,
  CONSTRAINT drug_equivalents_distinct_chk CHECK (source_drug_presentation_id <> target_drug_presentation_id),
  CONSTRAINT drug_equivalents_score_chk CHECK (equivalence_score >= 0 AND equivalence_score <= 100),
  CONSTRAINT drug_equivalents_unique UNIQUE (source_drug_presentation_id, target_drug_presentation_id, equivalence_type)
);

CREATE TABLE drug_interactions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  ingredient_a_id UUID NOT NULL,
  ingredient_b_id UUID NOT NULL,
  severity risk_level NOT NULL,
  mechanism TEXT,
  clinical_effect TEXT NOT NULL,
  recommendation TEXT NOT NULL,
  source_reference TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT drug_interactions_ingredient_a_fk FOREIGN KEY (ingredient_a_id) REFERENCES active_ingredients(id) ON DELETE CASCADE,
  CONSTRAINT drug_interactions_ingredient_b_fk FOREIGN KEY (ingredient_b_id) REFERENCES active_ingredients(id) ON DELETE CASCADE,
  CONSTRAINT drug_interactions_distinct_chk CHECK (ingredient_a_id <> ingredient_b_id),
  CONSTRAINT drug_interactions_order_chk CHECK (ingredient_a_id::TEXT < ingredient_b_id::TEXT),
  CONSTRAINT drug_interactions_unique UNIQUE (ingredient_a_id, ingredient_b_id)
);

CREATE TABLE contraindications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  active_ingredient_id UUID NOT NULL,
  condition_code TEXT NOT NULL,
  severity risk_level NOT NULL,
  details TEXT NOT NULL,
  source_reference TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT contraindications_ingredient_fk FOREIGN KEY (active_ingredient_id) REFERENCES active_ingredients(id) ON DELETE CASCADE,
  CONSTRAINT contraindications_condition_fk FOREIGN KEY (condition_code) REFERENCES clinical_conditions(code),
  CONSTRAINT contraindications_unique UNIQUE (active_ingredient_id, condition_code)
);

CREATE TABLE prescriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  source_country_code CHAR(2),
  source_language_code VARCHAR(10),
  file_name TEXT,
  storage_path TEXT,
  mime_type TEXT,
  file_size_bytes BIGINT,
  ocr_text TEXT,
  prescriber_name TEXT,
  prescribed_at DATE,
  processing_status prescription_processing_status NOT NULL DEFAULT 'uploaded',
  failure_reason TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT prescriptions_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT prescriptions_country_fk FOREIGN KEY (source_country_code) REFERENCES countries(code),
  CONSTRAINT prescriptions_language_fk FOREIGN KEY (source_language_code) REFERENCES supported_languages(code),
  CONSTRAINT prescriptions_file_size_chk CHECK (file_size_bytes IS NULL OR file_size_bytes >= 0)
);

CREATE TABLE prescription_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  prescription_id UUID NOT NULL,
  line_number INTEGER,
  raw_text TEXT NOT NULL,
  matched_drug_presentation_id UUID,
  confidence_score NUMERIC(5,2),
  dose_text TEXT,
  frequency_text TEXT,
  duration_text TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT prescription_items_prescription_fk FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE,
  CONSTRAINT prescription_items_presentation_fk FOREIGN KEY (matched_drug_presentation_id) REFERENCES drug_presentations(id),
  CONSTRAINT prescription_items_confidence_chk CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 100)),
  CONSTRAINT prescription_items_line_number_chk CHECK (line_number IS NULL OR line_number > 0)
);

CREATE TABLE user_medications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  drug_presentation_id UUID,
  prescription_item_id UUID,
  entered_name TEXT NOT NULL,
  dose_text TEXT,
  frequency_text TEXT,
  indication TEXT,
  instructions_simple TEXT,
  start_date DATE,
  end_date DATE,
  source medication_source NOT NULL DEFAULT 'manual',
  status medication_status NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT user_medications_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT user_medications_presentation_fk FOREIGN KEY (drug_presentation_id) REFERENCES drug_presentations(id),
  CONSTRAINT user_medications_prescription_item_fk FOREIGN KEY (prescription_item_id) REFERENCES prescription_items(id) ON DELETE SET NULL,
  CONSTRAINT user_medications_entered_name_chk CHECK (LENGTH(BTRIM(entered_name)) >= 2),
  CONSTRAINT user_medications_date_range_chk CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
);

CREATE TABLE medication_interaction_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  checked_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  medication_count INTEGER NOT NULL,
  highest_severity risk_level,
  result_summary TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT medication_interaction_checks_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT medication_interaction_checks_count_chk CHECK (medication_count >= 0)
);

CREATE TABLE medication_interaction_check_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  interaction_check_id UUID NOT NULL,
  user_medication_a_id UUID NOT NULL,
  user_medication_b_id UUID NOT NULL,
  drug_interaction_id UUID,
  severity risk_level NOT NULL,
  recommendation TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT med_interaction_check_items_check_fk FOREIGN KEY (interaction_check_id) REFERENCES medication_interaction_checks(id) ON DELETE CASCADE,
  CONSTRAINT med_interaction_check_items_med_a_fk FOREIGN KEY (user_medication_a_id) REFERENCES user_medications(id) ON DELETE CASCADE,
  CONSTRAINT med_interaction_check_items_med_b_fk FOREIGN KEY (user_medication_b_id) REFERENCES user_medications(id) ON DELETE CASCADE,
  CONSTRAINT med_interaction_check_items_interaction_fk FOREIGN KEY (drug_interaction_id) REFERENCES drug_interactions(id) ON DELETE SET NULL,
  CONSTRAINT med_interaction_check_items_distinct_chk CHECK (user_medication_a_id <> user_medication_b_id)
);

CREATE TABLE medical_passports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL,
  share_token UUID NOT NULL DEFAULT gen_random_uuid(),
  status passport_status NOT NULL DEFAULT 'draft',
  title TEXT NOT NULL DEFAULT 'Global Pharma Passport',
  expires_at TIMESTAMPTZ,
  last_shared_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT medical_passports_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT medical_passports_share_token_unique UNIQUE (share_token)
);

CREATE TABLE medical_passport_snapshots (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  medical_passport_id UUID NOT NULL,
  language_code VARCHAR(10) NOT NULL,
  version INTEGER NOT NULL,
  snapshot_json JSONB NOT NULL,
  generated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT medical_passport_snapshots_passport_fk FOREIGN KEY (medical_passport_id) REFERENCES medical_passports(id) ON DELETE CASCADE,
  CONSTRAINT medical_passport_snapshots_language_fk FOREIGN KEY (language_code) REFERENCES supported_languages(code),
  CONSTRAINT medical_passport_snapshots_version_chk CHECK (version > 0),
  CONSTRAINT medical_passport_snapshots_json_chk CHECK (jsonb_typeof(snapshot_json) = 'object'),
  CONSTRAINT medical_passport_snapshots_unique UNIQUE (medical_passport_id, language_code, version)
);

CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  country_code CHAR(2),
  billing_email CITEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT organizations_country_fk FOREIGN KEY (country_code) REFERENCES countries(code),
  CONSTRAINT organizations_name_chk CHECK (LENGTH(BTRIM(name)) >= 2)
);

CREATE TABLE organization_members (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  user_id UUID NOT NULL,
  role TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT organization_members_org_fk FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
  CONSTRAINT organization_members_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT organization_members_unique UNIQUE (organization_id, user_id)
);

CREATE TABLE subscriptions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID,
  organization_id UUID,
  plan_code TEXT NOT NULL,
  status subscription_status NOT NULL DEFAULT 'trialing',
  provider TEXT NOT NULL,
  provider_subscription_id TEXT,
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  cancel_at_period_end BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT subscriptions_user_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT subscriptions_org_fk FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
  CONSTRAINT subscriptions_owner_chk CHECK (
    (user_id IS NOT NULL AND organization_id IS NULL)
    OR (user_id IS NULL AND organization_id IS NOT NULL)
  ),
  CONSTRAINT subscriptions_period_chk CHECK (
    current_period_end IS NULL
    OR current_period_start IS NULL
    OR current_period_end >= current_period_start
  )
);

CREATE TABLE api_clients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  name TEXT NOT NULL,
  client_key TEXT NOT NULL UNIQUE,
  client_secret_hash TEXT NOT NULL,
  status api_client_status NOT NULL DEFAULT 'active',
  rate_limit_per_minute INTEGER NOT NULL DEFAULT 60,
  allowed_scopes TEXT[] NOT NULL DEFAULT '{}',
  last_used_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT api_clients_org_fk FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE,
  CONSTRAINT api_clients_name_chk CHECK (LENGTH(BTRIM(name)) >= 2),
  CONSTRAINT api_clients_rate_limit_chk CHECK (rate_limit_per_minute > 0)
);

CREATE TABLE api_usage_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  api_client_id UUID NOT NULL,
  endpoint TEXT NOT NULL,
  request_count INTEGER NOT NULL DEFAULT 1,
  status_code INTEGER,
  logged_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT api_usage_logs_client_fk FOREIGN KEY (api_client_id) REFERENCES api_clients(id) ON DELETE CASCADE,
  CONSTRAINT api_usage_logs_request_count_chk CHECK (request_count > 0),
  CONSTRAINT api_usage_logs_status_code_chk CHECK (status_code IS NULL OR (status_code >= 100 AND status_code <= 599))
);

CREATE TABLE audit_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_user_id UUID,
  organization_id UUID,
  event_name TEXT NOT NULL,
  target_table TEXT,
  target_id UUID,
  metadata JSONB NOT NULL DEFAULT '{}'::JSONB,
  ip_address INET,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT audit_events_actor_fk FOREIGN KEY (actor_user_id) REFERENCES users(id) ON DELETE SET NULL,
  CONSTRAINT audit_events_org_fk FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE SET NULL,
  CONSTRAINT audit_events_metadata_chk CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_country_code ON users(country_code);
CREATE INDEX idx_active_ingredients_atc_code ON active_ingredients(atc_code);
CREATE UNIQUE INDEX uq_active_ingredients_inn_name_ci ON active_ingredients (LOWER(inn_name));
CREATE INDEX idx_active_ingredients_inn_name_trgm ON active_ingredients USING GIN (inn_name gin_trgm_ops);
CREATE INDEX idx_drug_products_country_code ON drug_products(country_code);
CREATE UNIQUE INDEX uq_drug_products_country_brand_manufacturer_ci
  ON drug_products (country_code, LOWER(brand_name), COALESCE(LOWER(manufacturer), ''));
CREATE INDEX idx_drug_products_brand_name_trgm ON drug_products USING GIN (brand_name gin_trgm_ops);
CREATE INDEX idx_drug_presentations_product_id ON drug_presentations(drug_product_id);
CREATE UNIQUE INDEX uq_drug_presentations_signature_ci
  ON drug_presentations (drug_product_id, dosage_form_id, LOWER(strength_text), COALESCE(LOWER(route), ''));
CREATE INDEX idx_drug_presentation_ingredients_presentation_id ON drug_presentation_ingredients(drug_presentation_id);
CREATE INDEX idx_drug_presentation_ingredients_ingredient_id ON drug_presentation_ingredients(active_ingredient_id);
CREATE INDEX idx_drug_synonyms_synonym_trgm ON drug_synonyms USING GIN (synonym gin_trgm_ops);
CREATE INDEX idx_drug_equivalents_source ON drug_equivalents(source_drug_presentation_id);
CREATE INDEX idx_drug_equivalents_target ON drug_equivalents(target_drug_presentation_id);
CREATE INDEX idx_contraindications_ingredient ON contraindications(active_ingredient_id);
CREATE INDEX idx_prescriptions_user_id ON prescriptions(user_id);
CREATE INDEX idx_prescriptions_status ON prescriptions(processing_status);
CREATE INDEX idx_prescription_items_prescription_id ON prescription_items(prescription_id);
CREATE INDEX idx_user_medications_user_id ON user_medications(user_id);
CREATE INDEX idx_user_medications_status ON user_medications(status);
CREATE INDEX idx_user_medications_presentation_id ON user_medications(drug_presentation_id);
CREATE INDEX idx_medication_interaction_checks_user_id ON medication_interaction_checks(user_id);
CREATE INDEX idx_medical_passports_user_id ON medical_passports(user_id);
CREATE INDEX idx_medical_passports_status ON medical_passports(status);
CREATE INDEX idx_api_clients_org_id ON api_clients(organization_id);
CREATE INDEX idx_api_usage_logs_client_time ON api_usage_logs(api_client_id, logged_at DESC);
CREATE INDEX idx_audit_events_actor ON audit_events(actor_user_id);
CREATE INDEX idx_audit_events_created_at ON audit_events(created_at DESC);

CREATE TRIGGER set_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_user_profiles_updated_at
BEFORE UPDATE ON user_profiles
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_active_ingredients_updated_at
BEFORE UPDATE ON active_ingredients
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_drug_products_updated_at
BEFORE UPDATE ON drug_products
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_drug_presentations_updated_at
BEFORE UPDATE ON drug_presentations
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_drug_equivalents_updated_at
BEFORE UPDATE ON drug_equivalents
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_drug_interactions_updated_at
BEFORE UPDATE ON drug_interactions
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_contraindications_updated_at
BEFORE UPDATE ON contraindications
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_prescriptions_updated_at
BEFORE UPDATE ON prescriptions
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_prescription_items_updated_at
BEFORE UPDATE ON prescription_items
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_user_medications_updated_at
BEFORE UPDATE ON user_medications
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_medical_passports_updated_at
BEFORE UPDATE ON medical_passports
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_organizations_updated_at
BEFORE UPDATE ON organizations
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_subscriptions_updated_at
BEFORE UPDATE ON subscriptions
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER set_api_clients_updated_at
BEFORE UPDATE ON api_clients
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();

INSERT INTO supported_languages (code, name, is_rtl)
VALUES
  ('fr', 'French', FALSE),
  ('en', 'English', FALSE),
  ('ar', 'Arabic', TRUE)
ON CONFLICT (code) DO NOTHING;

INSERT INTO countries (code, name, phone_code)
VALUES
  ('FR', 'France', '+33'),
  ('MA', 'Morocco', '+212'),
  ('GB', 'United Kingdom', '+44'),
  ('US', 'United States', '+1')
ON CONFLICT (code) DO NOTHING;

COMMIT;

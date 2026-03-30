# Global Pharma Passport API

## Run locally

```bash
cd /Users/kawtar/Documents/New\ project\ 3/apps/api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
docker compose up -d
alembic upgrade head
uvicorn app.main:app --reload
```

Open the docs at `http://127.0.0.1:8000/api/v1/docs`.

Run tests:

```bash
pytest
```

Run tests by domain:

```bash
pytest tests/test_authentication.py
pytest tests/test_interactions.py
pytest tests/test_equivalents.py
pytest tests/test_main_api.py
```

## PostgreSQL local

This project is designed to run on PostgreSQL locally and in production.

Start the database:

```bash
docker compose up -d
```

Check that PostgreSQL is ready:

```bash
docker compose ps
```

Apply migrations:

```bash
alembic upgrade head
```

Load the Morocco-France MVP catalog:

```bash
python -m app.seeds.load_mvp_catalog
```

Rollback the initial migration if needed:

```bash
alembic downgrade -1
```

Connect manually with `psql`:

```bash
psql postgresql://postgres:postgres@localhost:5432/global_pharma_passport
```

## Environment

Copy `.env.example` to `.env` and update the connection string if needed.

Default local database:

- `postgresql+psycopg://postgres:postgres@localhost:5432/global_pharma_passport`

Override with:

```bash
export DATABASE_URL="postgresql+psycopg://user:password@localhost:5432/global_pharma_passport"
```

JWT settings:

```bash
export JWT_SECRET_KEY="replace-with-a-long-random-secret"
export ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

Security and deployment settings:

```bash
export ENVIRONMENT=production
export ALLOWED_ORIGINS="https://your-frontend-domain.com"
export TRUSTED_HOSTS="your-api-domain.com"
export FORCE_HTTPS=true
export DOCS_ENABLED=false
export LOG_LEVEL=INFO
export ENABLE_REQUEST_LOGGING=true
```

Private beta monitoring:

- use `/health` for uptime checks
- keep `ENABLE_REQUEST_LOGGING=true` to log method, path, status, request ID, and duration
- set `LOG_LEVEL=INFO` in beta and raise to `WARNING` if logs become noisy
- use the `X-Request-ID` response header to correlate user-reported issues with backend logs

Stripe settings:

```bash
export APP_BASE_URL="https://your-app-domain.com"
export STRIPE_SECRET_KEY="sk_live_or_test"
export STRIPE_WEBHOOK_SECRET="whsec_..."
export STRIPE_PREMIUM_MONTHLY_PRICE_ID="price_..."
```

## Migrations

The canonical production migration lives in:

- [001_init_global_pharma_passport.sql](/Users/kawtar/Documents/New%20project%203/apps/api/db/migrations/001_init_global_pharma_passport.sql)
- [001_init_global_pharma_passport_down.sql](/Users/kawtar/Documents/New%20project%203/apps/api/db/migrations/001_init_global_pharma_passport_down.sql)
- [20260329_0001_init_global_pharma_passport.py](/Users/kawtar/Documents/New%20project%203/apps/api/alembic/versions/20260329_0001_init_global_pharma_passport.py)
- [20260329_0002_add_auth_fields.py](/Users/kawtar/Documents/New%20project%203/apps/api/alembic/versions/20260329_0002_add_auth_fields.py)
- [20260329_0003_add_billing_fields.py](/Users/kawtar/Documents/New%20project%203/apps/api/alembic/versions/20260329_0003_add_billing_fields.py)

Alembic executes the SQL migration exactly, which keeps the PostgreSQL schema explicit and production-friendly.

## Main endpoints

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `GET /api/v1/billing/me/subscription`
- `GET /api/v1/billing/me/entitlements`
- `POST /api/v1/billing/checkout-session`
- `POST /api/v1/billing/portal-session`
- `POST /api/v1/billing/webhooks/stripe`
- `POST /api/v1/analytics/track`
- `GET /api/v1/analytics/dashboard`
- `POST /api/v1/users`
- `GET /api/v1/users`
- `GET /api/v1/users/me/profile`
- `PATCH /api/v1/users/me/profile`
- `POST /api/v1/medications/ingredients`
- `POST /api/v1/medications/dosage-forms`
- `POST /api/v1/medications/products`
- `GET /api/v1/medications/me`
- `POST /api/v1/medications/me`
- `PATCH /api/v1/medications/me/{medication_id}`
- `DELETE /api/v1/medications/me/{medication_id}`
- `POST /api/v1/interactions`
- `POST /api/v1/interactions/check`
- `GET /api/v1/passport/me`
- `GET /api/v1/passport/shared/{share_token}`
- `POST /api/v1/international-equivalents`
- `GET /api/v1/international-equivalents/search/{presentation_id}`

## Access model

- `auth/*` is for patient authentication.
- `medications/me` and `users/me/profile` require a bearer token.
- catalog write endpoints such as ingredient creation, product creation, interaction creation, and equivalent creation require an `admin` user.

## Freemium model

Current backend defaults every new user to the `free` plan automatically.

Free:

- up to 3 medications
- 1 international equivalent result per search
- travel mode reserved for premium

Premium:

- unlimited medications
- unlimited equivalent search results
- travel mode enabled

This keeps the product easy to launch while making the upgrade path obvious.

## Product analytics

The project now includes a first-party product tracking layer:

- backend ingestion via `POST /api/v1/analytics/track`
- internal metrics via `GET /api/v1/analytics/dashboard`
- event storage in `product_events`

It is designed to measure:

- total users
- retention proxies via returning activity
- feature usage by event
- free to paid conversion

Important privacy rule:

- do not send PHI or patient-sensitive content in analytics properties
- the backend sanitizes common sensitive keys before storing events

## Security posture

Current protections added in the backend:

- JWT tokens now include issuer, audience, issue time, not-before, expiry, and token ID
- runtime guard blocks the default JWT secret in production
- CORS and trusted host restrictions are configurable
- optional HTTPS redirect can be enabled in production
- security headers are added on every response
- all API responses include a request ID for safer debugging
- validation errors are sanitized into a controlled format
- unexpected server errors return a generic message instead of leaking internals
- Pydantic request schemas now forbid unexpected fields
- passwords require stronger complexity
- country and language codes are normalized and validated
- auth responses are marked `no-store` to reduce token caching risk

RGPD / HIPAA-like guidance already reflected in the code:

- minimize returned data: password hashes are never exposed
- avoid sensitive error leakage
- keep auth and billing responses non-cacheable
- structure the app so access control remains server-side

Still recommended before handling real patient traffic at scale:

- database encryption at rest managed by your provider
- encrypted backups
- audit logging for sensitive record access
- key rotation policy
- retention/deletion workflows for patient data
- signed BAAs and vendor review if you move toward real HIPAA obligations

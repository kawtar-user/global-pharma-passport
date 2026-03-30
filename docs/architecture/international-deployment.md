# International Readiness and Deployment

## What was prepared

### Frontend

- locale-aware routing under `apps/web/src/app/[locale]`
- supported locales: `fr`, `en`, `ar`
- locale middleware redirects `/` to `/<locale>`
- dictionary-based content layer in `apps/web/src/lib/i18n.ts`
- RTL support for Arabic via `dir="rtl"`

### Backend

- request context resolution from `Accept-Language` and `X-Country-Code`
- supported language and country registry in `apps/api/app/core/international.py`
- meta endpoints for countries, languages, and resolved request context
- default language/country controlled by environment

### Deployment

- frontend Vercel config in `apps/web/vercel.json`
- backend Docker image in `apps/api/Dockerfile`
- Render blueprint in `render.yaml`

## Global data model guidance

The PostgreSQL schema is already globally oriented because it separates:

- active ingredients
- commercial products
- presentations
- dosage forms
- country mappings
- international equivalents

This is the right scalable shape for worldwide expansion because:

- the same brand can differ by country
- the DCI stays the international anchor
- equivalence can be computed at the presentation level

## Production deployment steps

### 1. Prepare managed services

Create:

- one PostgreSQL production database
- one Vercel project for `apps/web`
- one backend service for `apps/api`
- one Stripe account/product/price if billing is enabled

### 2. Deploy the backend

Recommended simple path:

- use Render with the root blueprint `render.yaml`
- set the backend root directory to `apps/api`
- provide production environment variables

Required backend env vars:

- `ENVIRONMENT=production`
- `DATABASE_URL=...`
- `JWT_SECRET_KEY=...`
- `JWT_ISSUER=global-pharma-passport-api`
- `JWT_AUDIENCE=global-pharma-passport-clients`
- `ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app`
- `TRUSTED_HOSTS=your-api-domain.onrender.com`
- `FORCE_HTTPS=true`
- `DOCS_ENABLED=false`
- `APP_BASE_URL=https://your-frontend-domain.vercel.app`
- optional Stripe keys

After the first deploy:

- run `alembic upgrade head`
- confirm `GET /health` returns `200`

### 3. Deploy the frontend on Vercel

In Vercel:

- import the repository
- set project root to `apps/web`
- keep the default Next.js build settings or use `vercel.json`

Required frontend env vars:

- `NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.onrender.com/api/v1`
- `NEXT_PUBLIC_DEFAULT_LOCALE=fr`

### 4. Wire domains

Use:

- frontend custom domain on Vercel
- backend API domain on Render or your own subdomain

Recommended:

- `app.globalpharmapassport.com` for frontend
- `api.globalpharmapassport.com` for backend

### 5. Verify international behavior

Check:

- `/fr`, `/en`, `/ar` routes load
- Arabic layout renders RTL
- API `/api/v1/meta/languages`
- API `/api/v1/meta/countries`
- API `/api/v1/meta/request-context` with different headers

### 6. Final launch checklist

- production JWT secret rotated
- docs disabled
- HTTPS forced
- CORS restricted to production frontend
- migrations applied
- billing price IDs configured if premium is live
- error monitoring connected

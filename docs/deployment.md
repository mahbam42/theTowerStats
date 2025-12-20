# Deployment (Railway)

This page is Developer Documentation.

## Overview

theTowerStats is designed to run in local development with SQLite and in production with environment-driven settings.
For production, secrets must be provided via environment variables and Django’s `check --deploy` should pass without warnings.

## Required environment variables

- `DJANGO_DEBUG`:
  - Set to `0` in production.
- `DJANGO_SECRET_KEY`:
  - A secure, non-default secret key.
- `DJANGO_ALLOWED_HOSTS`:
  - Comma-separated hostnames (for example: `example.com,app.example.com`).
- `DJANGO_CSRF_TRUSTED_ORIGINS`:
  - Comma-separated origins including scheme (for example: `https://example.com`).
- `DATABASE_URL`:
  - SQLite for local development or Postgres in production (Railway provides this for Postgres services).

Optional overrides:

- `DJANGO_SECURE_HSTS_SECONDS` (default `3600` in production)
- `DJANGO_SECURE_SSL_REDIRECT` (default enabled in production)
- `DJANGO_SESSION_COOKIE_SECURE` (default enabled in production)
- `DJANGO_CSRF_COOKIE_SECURE` (default enabled in production)
- `DJANGO_USE_X_FORWARDED_HOST` (default enabled in production)
- `DJANGO_DB_CONN_MAX_AGE` (default `60` in production)

## Railway runtime

theTowerStats includes a `Procfile` suitable for Railway’s Django process model:

- Web process uses Gunicorn with `theTowerStats.wsgi:application`
- Bind address uses the platform-provided `PORT`

## Dependencies

Production installs runtime dependencies from `requirements.txt`.
Development and documentation tooling lives in `requirements-dev.txt` and is not required at runtime.

## Production validation

Run the deployment checklist locally (with production-style environment variables):

1. Set `DJANGO_DEBUG=0`.
2. Set `DJANGO_SECRET_KEY` and host/origin variables.
3. Run `manage.py check --deploy --fail-level WARNING`.

## Static files

Static assets are served via Django staticfiles and WhiteNoise in production.

Recommended workflow:

1. Run `manage.py collectstatic --noinput` during build/deploy.
2. Serve static files from the application process (WhiteNoise) unless a dedicated CDN is configured.

## PostgreSQL migration path (SQLite → Postgres)

This migration is intended to be schema-neutral and behavior-neutral:

1. Deploy the same code revision to both environments.
2. Run migrations in the Postgres environment.
3. Export data from the SQLite environment using `dumpdata`.
4. Import the exported data into Postgres using `loaddata`.
5. Validate record counts and spot-check key dashboards.

Recommended commands:

- Export (from SQLite):
  - `python manage.py dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.permission -e admin.logentry -e sessions.session --indent 2 -o sqlite-export.json`
- Import (to Postgres):
  - `python manage.py loaddata sqlite-export.json`

Notes:

> ⚠️ Caution
> This project preserves raw ingested data. Avoid transforms during migration.
> Treat migration as a transfer of serialized rows, not as a “re-interpretation” step.

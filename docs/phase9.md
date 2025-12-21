# Phase 9 — Developer / Progress Document

## Purpose

Phase 9 focused on production readiness and trust boundaries: deploying safely, tightening authorization scaffolding, and ensuring the app behaves predictably under production settings.

## Deployment

- Added deployment-oriented validation using Django’s `check --deploy` with production-style environment variables.
- Documented Railway runtime expectations and environment configuration in `docs/deployment.md`.
- Standardized the base template to reference local static assets (`core/app.css`, `core/app.js`) for predictable production serving.

## Trust Closure and Permission Scoping

- Introduced default auth groups (`player`, `admin`) and assigned model permissions during `post_migrate`.
- Ensured new users join the `player` group automatically on signup.
- Used permissions as a coarse capability layer while preserving per-player scoping as the primary isolation mechanism.

## Cleanup Outcomes

- Consolidated “production boot” expectations into reproducible checks and tests.
- Reduced reliance on environment-specific behavior by making host and origin handling explicit in production configuration.

## Notes and Limitations

- Group permissions do not replace per-player queryset scoping; both are required for safe behavior.
- Production checks validate configuration but do not validate data correctness or analysis results.

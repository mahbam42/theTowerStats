# Phase 10 — Developer / Progress Document

## Purpose

Phase 10 is a refinement pass focused on stabilizing the product surface and release hygiene for v0.2.0, without changing analysis semantics, metrics, or data meaning.

## Release Hygiene

- Updated public-facing documentation to match current behavior (`readme.md`).
- Introduced a SemVer-oriented changelog with explicit phase linking (`CHANGELOG.md`).
- Added/standardized local validation entry points (`scripts/checks`) and ensured documentation builds in CI (`.github/workflows/docs.yml`).
- Extended CI coverage to newer Python versions for earlier compatibility signals (`.github/workflows/django.yml`).

## Test Suite Health (Markers and Enforcement)

- Formalized a two-axis marker taxonomy:
  - Speed markers (required; exactly one): `unit`, `integration`
  - Semantic markers (optional): `regression`, `golden`
- Enabled strict marker behavior and documented intent in `pytest.ini`.
- Added a collection-time enforcement guard so unmarked (or multiply-marked) tests fail deterministically (`tests/conftest.py`).
- Split CI test execution into a fast unit job and a full suite job (`.github/workflows/django.yml`).
- Documented how to run and interpret markers in Developer Docs (`docs/development.md`).

## Battle History — Tournament Run Classification (Derived)

- Implemented derived tournament detection based on the Battle Report Tier label format (e.g. `3+`, `5+`, `8+`) in `core/tournament.py`.
- Exposed tournament metadata as view-layer fields (e.g. `is_tournament`, `tournament_bracket`) without adding persisted fields or migrations.
- Defaulted analytics and the Battle History table to exclude tournament runs, with explicit opt-in via an “Include tournaments” filter (`core/forms.py`, `core/views.py`, `core/templates/core/battle_history.html`, `core/templates/core/dashboard.html`).
- Added visual affordances for tournament rows (row styling and badges) to reduce accidental interpretation mixing (`core/static/core/app.css`).

## UX and Interaction Refinements

- Standardized a small design scale and shared tokens (spacing, font sizes, radii, neutral surfaces) in `core/static/core/app.css`.
- Reduced primary navigation to a small set of top-level destinations and moved secondary pages under a “More” menu (`core/templates/core/base.html`).
- Added a global search affordance with a lightweight results dropdown for quick navigation (`core/templates/core/base.html`, `core/templates/core/search.html`, `core/static/core/app.css`).
- Restructured the Charts dashboard controls to keep context filters visible and move optional controls behind disclosure (`core/templates/core/dashboard.html`).

## Notes and Limitations

- Tournament classification is heuristic and derived from raw Battle Report text; it assumes the Tier label continues to use the `N+` convention for tournaments.
- Marker enforcement is intentionally strict; test authors must choose `unit` or `integration` for every test to avoid accidental slow or flaky coverage creeping into the fast lane.


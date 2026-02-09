# Testing

This page is **Developer Documentation**. It describes how the automated test suite is structured and how to run it.

## Overview

The test suite is intentionally split by speed and semantics so maintainers can run the right level of validation for a change.

## Speed Markers (Required)

Every test must have exactly one speed marker:

- `@pytest.mark.unit`
  - Pure, deterministic tests
  - No database access
- `@pytest.mark.integration`
  - Any test that uses Django, the database, views, management commands, or IO

Run just unit tests:

```bash
pytest -m unit
```

Run just integration tests:

```bash
pytest -m integration
```

Run the full suite (unit + integration):

```bash
pytest
```

## Test Database

Local test runs default to SQLite to avoid requiring a Postgres role with
database-creation privileges. CI still uses Postgres because `GITHUB_ACTIONS`
is set in GitHub Actions.

Override the test database when needed:

- Force a specific database URL:
  - `DJANGO_TEST_DATABASE_URL=postgresql://... pytest`
- Opt out of SQLite and use `DATABASE_URL` as-is:
  - `DJANGO_TEST_USE_SQLITE=0 pytest`

## Semantic Markers (Optional)

Optionally, add one semantic marker:

- `@pytest.mark.regression` for bug/regression coverage
- `@pytest.mark.golden` for snapshot/fixture-driven “golden” tests

## Canonical Examples

- Unit + golden: `tests/test_battle_report_parser.py`
- Integration: `tests/test_battle_history_table.py`
- Unit + regression: `tests/test_phase9a_uw_runs_count_utility.py`

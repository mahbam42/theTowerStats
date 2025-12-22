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

## Semantic Markers (Optional)

Optionally, add one semantic marker:

- `@pytest.mark.regression` for bug/regression coverage
- `@pytest.mark.golden` for snapshot/fixture-driven “golden” tests

## Canonical Examples

- Unit + golden: `tests/test_battle_report_parser.py`
- Integration: `tests/test_battle_history_table.py`
- Unit + regression: `tests/test_phase9a_uw_runs_count_utility.py`


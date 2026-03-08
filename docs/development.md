# Development

This page is **Developer Documentation**. It collects operational notes and local workflow details for maintainers.

## Dependencies

Install runtime dependencies:

```bash
pip install -r requirements.txt
```

Install development + documentation tooling:

```bash
pip install -r requirements-dev.txt
```

## Quality checks

Run the full local validation suite (lint, types, tests):

```bash
./scripts/checks
```

If you want `checks` available in your virtualenv's `PATH`, create a symlink:

```bash
ln -sf ../../scripts/checks .venv/bin/checks
```

## Testing

Testing conventions, markers, and running instructions are documented on the dedicated Testing page.

See: [Testing](testing.md)

## Production Snapshot (Local)

Use the refresh script to pull a read-only production snapshot into your local database and prune to a single player:

```bash
.venv/bin/python scripts/refresh_staging_db.py --player-display-name mahbam42
```

The script reads `.env` by default and expects `PROD_READONLY_DATABASE_URL` and `LOCAL_DATABASE_URL` to be set. For the manual workflow and grant setup, see `archive/stagingDB.md`.

Local Django entry points now also read `.env` automatically. If `DATABASE_URL` in `.env` points at the same local Postgres database as `LOCAL_DATABASE_URL`, `python manage.py runserver` will read the refreshed snapshot without needing a manual `export DATABASE_URL=...`.

## Repository docs in MkDocs

MkDocs includes repo-root GitHub Markdown files (for example, `CHANGELOG.md` and
`CONTRIBUTING.md`) via `mkdocs-gen-files` instead of symlinks.

To add another repo document:

1. Add the filename to `REPO_FILES` in `scripts/mkdocs_gen_repo_docs.py`.
2. Add a matching entry under the `Project` section in `mkdocs.yml`.

Guided Walkthrough testing note: if the walkthrough does not appear in demo mode, clear local storage keys `tts_walkthrough_dismissed` and `tts_walkthrough_completed_at` via DevTools → Application → Local Storage for the current site.

## Migrations

If Django reports conflicting migrations (multiple leaf nodes in an app), create a merge migration and commit it.

```bash
python manage.py makemigrations --merge
python manage.py migrate
```

## Chart configuration

The Charts dashboard is driven by declarative `ChartConfig` entries and a central `MetricSeries` registry.

- Metric keys and capabilities are declared in `analysis/series_registry.py`.
- Built-in charts are declared in `core/charting/configs.py` and validated at import time.
- `core/charting/validator.py` enforces strict rules so future Chart Builder output fails fast with clear errors.

### Derived formulas

- Formulas may use numeric constants, metric-key identifiers, unary `+/-`, and binary `+ - * /` only.
- All identifiers must be registered metric keys and must also appear in the chart’s `metric_series`.
- `derived.x_axis` must match the referenced metrics’ time index (`time` → `timestamp`, `wave_number` → `wave_number`).

### Comparisons

- Comparison modes other than `none` are only allowed when `category="comparison"`.
- `by_tier` and `by_preset` require every metric series to support that dimension.
- `by_entity` requires `comparison.entities` and exactly one entity filter enabled (`uw`, `guardian`, or `bot`).

## Explore summaries

- Farming efficiency by tier compares each tier to the nearest available tier when building deltas and plateau checks, while still warning about missing tiers.

## Explore query templates

- Explore query templates are stored in the database and managed through Django Admin.
- Templates are global, not player-scoped.
- Explore only lists templates where `is_active=True`, ordered alphabetically by name.
- Templates are copied into the editor and remain editable before the player runs or saves them.

## Event window helpers

- Shared Event-window calculations live in `analysis/event_windows.py`.
- Use the shared helper instead of duplicating the Event anchor date in dashboard-specific code paths.

## Time semantics

- **Real time** comes from the Battle Report’s “Real Time” field and is used for per-hour rates such as coins/real hour.
- **In-game timing** (cooldowns and durations) is shown in seconds and is sourced from the external wiki tables.
- **Accelerated time** can make real-world time diverge from in-game seconds (for example, due to speed effects); dashboards must label units explicitly.
- Wiki-derived timing values are treated as reference data and may be inaccurate or drift over time.

## Attributions

- Per-hour resource metrics (cells/hour, reroll shards/hour) requested by u/BoxersOrCaseBriefs.

## Multi-player scoping

Phase 8 introduces first-class multi-player support.

- Every player-owned or mutable row is linked to `Player`, and `Player` is a 1:1 extension of the Django auth user.
- Views must derive the Player from `request.user` and must not accept a `player_id` from the client.
- Queryset filtering is mandatory for correctness and isolation; permissions are not a substitute for filtering.
- Admin pages must scope querysets to `player__user=request.user` for non-superusers and must assign `player` automatically on create.

## Security notes

- Post actions that accept `next` must validate the URL before redirecting. Use `core.redirects.safe_redirect` for any redirect derived from user input.
- AJAX error payloads should avoid raw exception details and return a user-safe message in production.

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

## Time semantics

- **Real time** comes from the Battle Report’s “Real Time” field and is used for per-hour rates such as coins/real hour.
- **In-game timing** (cooldowns and durations) is shown in seconds and is sourced from the external wiki tables.
- **Accelerated time** can make real-world time diverge from in-game seconds (for example, due to speed effects); dashboards must label units explicitly.
- Wiki-derived timing values are treated as reference data and may be inaccurate or drift over time.

## Multi-player scoping

Phase 8 introduces first-class multi-player support.

- Every player-owned or mutable row is linked to `Player`, and `Player` is a 1:1 extension of the Django auth user.
- Views must derive the Player from `request.user` and must not accept a `player_id` from the client.
- Queryset filtering is mandatory for correctness and isolation; permissions are not a substitute for filtering.
- Admin pages must scope querysets to `player__user=request.user` for non-superusers and must assign `player` automatically on create.

## Security notes

- Post actions that accept `next` must validate the URL before redirecting. Use `core.redirects.safe_redirect` for any redirect derived from user input.
- AJAX error payloads should avoid raw exception details and return a user-safe message in production.

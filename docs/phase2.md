# Phase 2: Context + Comparisons

This page is **Developer Documentation**. It summarizes Phase 2 deliverables and constraints for maintainers.

Phase 2 adds contextual analysis on top of the Phase 1 pipeline while staying
neutral (facts, not advice).

## Dashboard UI (`/`)

### Context filters (GET)

The chart view supports contextual filtering:

- `start_date`, `end_date` (inclusive)
- `tier` (exact match)
- `preset` (preset tag primary key)

Filters affect:

- the Analysis Engine inputs (filtered queryset),
- the chart output (labels + datasets).

### Preset labels (minimal)

Runs can be labeled with an optional preset:

- Import form (POST): `preset_name` (creates/uses `player_state.models.Preset`)
- Stored on `gamedata.models.BattleReportProgress.preset`

Presets are labels only (no enforced limits, no ranking, no recommendations).

### Chart overlays (GET)

The same metric can be overlaid as multiple datasets:

- `overlay_group=none` (default): single dataset
- `overlay_group=tier`: one dataset per tier in the current context
- `overlay_group=preset`: one dataset per preset in the current context (including “No preset”)

Optional moving average overlay:

- `moving_average_window` (integer, `>= 2`)

### Chart usability (Phase 2.5)

- Active context is shown in a sticky summary bar and updates live as filters change.
- Legend entries can be clicked to toggle individual datasets on/off.
- Tooltips show exact `coins/hour` values plus the current context (date range, filters, overlays).
- Missing dates are rendered as gaps (lines do not connect across missing data).

### Delta comparisons (GET)

Deltas are computed on demand and are never persisted:

- Run vs run: `run_a`, `run_b` (BattleReport primary keys)
- Window vs window:
  - `window_a_start`, `window_a_end`
  - `window_b_start`, `window_b_end`

Comparisons run within the current tier/preset context, but do not depend on the
chart `start_date`/`end_date` filters (the window dates control inclusion).

Currently displayed delta metric:

- coins/hour (absolute + percent)

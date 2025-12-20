# Phase 4 — Parameterized Effects & Derived Metrics

This page is **Developer Documentation**. It summarizes Phase 4 deliverables and constraints for maintainers.

Phase 4 extends the Analysis Engine to combine:

- observed run data (Battle Reports), and
- versioned, wiki-derived parameter tables (stored as immutable revisions),

to compute **derived metrics** on demand.

This phase answers: “What does this mechanic imply numerically?”
It does **not** answer: “What should the player do?”

### Key Rules

- **No persistence of derived metrics**: derived values are computed at request time.
- **Revision safety**: parameter revisions are treated as immutable; analysis explicitly chooses which revision(s) to use.
- **Traceability**: derived metric output includes the raw parameter strings and (when available) the `WikiData` revision ids used.

### Parameter Revision Selection

The core app selects wiki-derived parameter values by choosing a `WikiData` row for each (entity, level, star) row in upgrade tables. A single “latest” revision is chosen using:

1. `WikiData.last_seen` (descending), then
2. `WikiData.id` (descending) as a tie-breaker.

The selection policy is surfaced in the UI whenever a derived metric is charted.

### Entity Selection

Entity-scoped derived metrics (bots, ultimate weapons, guardian chips) require an explicit entity selection in the chart context form.
If no entity is selected, the derived metric value is returned as `None` and the UI displays the missing-context assumption.

### Chartable Metrics

Metrics are exposed in the Charts form as either:

- **observed** (directly computed from run data), or
- **derived** (computed from observed data + selected parameters).

Currently supported metric keys:

- `coins_per_hour` (observed)
- `uw_uptime_percent` (derived)
- `uw_effective_cooldown_seconds` (derived)
- `guardian_activations_per_minute` (derived)
- `bot_uptime_percent` (derived)

### Supported Parameter Keys (Initial Set)

Derived metrics intentionally depend on a small, explicit set of parameter keys.
Unknown keys are ignored and missing context results in partial outputs (None values).

- `cooldown`: cooldown as seconds (e.g. `120`)
- `duration`: duration as seconds (e.g. `30`)

### Formulas (Non-Prescriptive)

- Ultimate Weapon uptime:
  - `uptime% = 100 * clamp(duration / cooldown, 0..1)`
- Ultimate Weapon effective cooldown:
  - `effective_cooldown_seconds = cooldown_seconds`
- Guardian activations/minute:
  - `activations/min = 60 / cooldown_seconds`
- Bot uptime:
  - `uptime% = 100 * clamp(duration / cooldown, 0..1)`

### Revision Selection (As-Of)

Derived metrics may be computed using either:

- **latest**: the most recently observed `WikiData` row per (entity, level, star), or
- **as-of**: the most recent row where `WikiData.last_seen <= wiki_as_of`.

The selected `WikiData` primary keys are surfaced alongside derived metric output so
historical runs can be re-analyzed against the exact same revision inputs.

### Charting Validation (Phase 4 → 5 Bridge)

When charting a **derived** metric on the Charts dashboard, the UI renders a
second, adjacent **observed** chart (`coins_per_hour`) using the same Tier/Date
Range filters. This is a visual-only validation that:

- derived metrics are computed at request time (no persistence), and
- derived output references versioned wiki parameters (revision ids shown under
  “Parameters referenced”).

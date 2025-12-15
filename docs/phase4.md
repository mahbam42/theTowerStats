## Phase 4 — Parameterized Effects & Derived Metrics

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

The core app selects parameter rows by their `source_wikidata` foreign key. A single “latest” revision is chosen per entity type/name using:

1. `WikiData.last_seen` (descending), then
2. `WikiData.id` (descending) as a tie-breaker.

The selection policy is surfaced in the UI whenever a derived metric is charted.

### Chartable Metrics

Metrics are exposed in the Charts form as either:

- **observed** (directly computed from run data), or
- **derived** (computed from observed data + selected parameters).

Currently supported metric keys:

- `coins_per_hour` (observed)
- `coins_per_hour_effective_multiplier` (derived)
- `coins_per_hour_ev_simulated` (derived, deterministic Monte Carlo)
- `effective_cooldown_seconds` (derived)

### Supported Parameter Keys (Initial Set)

Derived metrics intentionally depend on a small, explicit set of parameter keys.
Unknown keys are ignored and missing context results in partial outputs (None values).

- `coins_multiplier`: multiplier factor as `x1.15` (multiplier parsing)
- `coins_bonus_percent`: percent as `15%` (treated as `1 + 0.15`)
- `proc_chance`: probability as `25%` (stored as `0.25`)
- `proc_multiplier`: proc multiplier as `x2`
- `base_cooldown_seconds`: base cooldown as seconds (e.g. `120`)
- `cooldown_reduction_percent`: cooldown reduction as percent (e.g. `10%`)

### Formulas (Non-Prescriptive)

- Effective cooldown:
  - `effective = base * (1 - sum(reductions))`, clamped to `>= 0`
- Simulated EV multiplier (Bernoulli proc):
  - independent trials with seeded RNG (see chart form fields `EV trials` and `EV seed`)
  - expected multiplier is the mean multiplier observed across trials


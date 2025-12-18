# Phase 6 Concepts

This page is **Developer Documentation**. It describes internal conventions used to keep analysis outputs deterministic, testable, and safe to display.

## Units (Validation + Formatting)

Phase 6 introduces a strict **unit contract** for any value displayed in dashboards.

### Goals

- Prevent ambiguous values from being interpreted as the wrong kind of number.
- Ensure every displayed metric has an explicit unit category.
- Keep parsing deterministic and testable.

### Rules

- Values parsed from Battle Reports must be validated against an expected `UnitType`.
- Multiplier formats (`x1.15`, `15%`) must **not** be accepted for non-multiplier contracts.
- Compact magnitudes (`K`, `M`, `B`, `T`) must normalize deterministically.

### Implementation Notes

- Best-effort parsing lives in `analysis/quantity.py`.
- Fail-fast validation lives in `analysis/units.py` via `UnitContract` and `parse_validated_quantity`.

## Metric Categories

Every metric belongs to **exactly one** semantic category:

`MetricCategory = { economy, combat, fetch, utility }`

These categories are:

- **Semantic**: they describe meaning, not chart type or color.
- **Exhaustive**: no chartable metric may exist outside the registry.

## Donut Charts (Why)

Some Phase 6 metrics are best understood as **breakdowns** rather than trends.

Donut charts are used when:

- The total is meaningful and deterministic within the selected context.
- The user benefit comes from *composition* (what contributed) rather than *change over time*.

Examples:

- Coins earned by source (Battle Report utility + Guardian rollups).
- Guardian fetch outputs (gems/shards/modules) within the selected context.

## Context and Precedence

Context inputs are used to scope which runs are included in analysis output. Context changes must **never** change metric meaning—only which runs are included.

### Precedence

Context filters are applied in this order:

1. Date range
2. Preset
3. Tier

### Empty States

- Empty scopes must return typed-but-empty chart outputs (empty labels/datasets).
- No silent fallbacks (e.g., “preset had no runs so we used tier-only”).

### Rolling Windows

Rolling windows are applied *after* context filters:

- Last N runs
- Last N days

This keeps window behavior consistent across different contexts.

## Base Value vs Effective Value

Many player-facing parameters have both:

- **Base value**: the raw value from the selected parameter level.
- **Effective value**: the value after applying modifiers (cards, labs, relics, etc.).

Effective values reflect what actually occurs in a run. Modifier explanations are provided for clarity and may not list every contributing effect.

Phase 6’s intent is that every parameter row can explain:

- Base value
- Effective value
- At least one modifier contribution (e.g., “+X% from Cards”)

This work is tracked as a Phase 6 deliverable to ensure later comparisons and higher-order analysis remain explainable.

# Phase 7 — Developer / Progress Summary

## Purpose

Phase 7 (“Power Tools”) shifts the app from descriptive dashboards to deterministic, schema-driven tooling that remains explainable and non-prescriptive.

## What Was Added

### Chart Builder Contract (DTO → Validation → Analysis)

- Introduced `ChartConfigDTO` as a first-class, versioned configuration for ad-hoc charts.
- Centralized validation in `validate_chart_config_dto` (units, category mixing, donut constraints, comparison scopes, smoothing capability).
- Added an analysis execution path that consumes `ChartConfigDTO` and returns chart-ready DTO outputs only (no persistence, no ORM writes from analysis).

### Snapshot System (Reusable, Immutable)

- Snapshots persist a versioned `ChartConfigDTO` payload (`ChartSnapshot.config`) plus a dashboard `target`.
- Snapshot immutability is enforced at the model layer.
- Snapshot loading applies saved builder configuration back into the dashboard query state.
- Snapshot encoding is JSONField-safe (dates stored as ISO strings) to preserve deterministic replays.

### Cross-Dashboard Snapshot Reuse (Phase 7 Scope)

- Implemented snapshot rendering on the Ultimate Weapons progress dashboard (SNAP_04 “UWs first”).
- The UW dashboard renders the selected snapshot chart inline above the progress table (Option A).

### Data Quality Flags (Patch Boundaries)

- Added an admin-managed patch boundary model to represent known boundaries explicitly.
- Charts surface boundary flags as deterministic tooltip reasons without modifying metric values.

### Advice Layer (Read-only, Non-prescriptive)

- Advice remains descriptive and forbids prescriptive tokens.
- Added snapshot-based advice comparisons:
  - Snapshot vs current filters
  - Snapshot vs snapshot
- Advice deterministically degrades to “Insufficient data” when either scope has fewer than 3 runs.

## Key Files

- DTO + analysis: `analysis/chart_config_dto.py`, `analysis/chart_config_validator.py`, `analysis/chart_config_engine.py`
- Snapshots: `player_state/models.py` (`ChartSnapshot`), `core/charting/snapshot_codec.py`
- Dashboard wiring: `core/views.py`, `core/templates/core/dashboard.html`
- UW snapshot reuse: `core/views.py`, `core/templates/core/ultimate_weapon_progress.html`
- Patch boundaries: `definitions/models.py`, `definitions/admin.py`
- Advice: `core/advice.py`

## Tests and Validation

- Added/updated Phase 7 tests for DTO contract, snapshot reuse, advice degradation, and patch boundary flags.
- Validation gates: `ruff`, `mypy`, `pytest` are expected to pass for Phase 7 completion.

## Phase 8 Dependencies / Notes

- `ChartSnapshot.target` and versioned `ChartConfigDTO` payloads are intended to support multi-player isolation and broader snapshot reuse in Phase 8.
- Advice remains intentionally minimal in Phase 7 and should expand only by consuming existing DTO outputs (no new math).


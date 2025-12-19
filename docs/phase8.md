# Phase 8 — Developer / Progress Document

## Purpose

Phase 8 introduces multi-player isolation as a system-level invariant, then builds goal-aware (still non-prescriptive) comparative advice and low-risk adoption features on top.

## Why Multi-Player Support Was Introduced

Prior phases assumed a single local dataset. As the app gained snapshots, progress dashboards, and richer analysis, the risk of cross-user data exposure increased and the cost of retrofitting isolation later grew.

Phase 8 formalizes a single rule: **every mutable, player-owned record is scoped to exactly one Player, and views never accept a player id from the client**.

## Pillar 1 — Player Isolation (Multi-Player)

### Models (Ownership and Separation)

- Introduced a `Player` model as a 1:1 extension of the auth user.
- Added a `player` foreign key to all mutable, player-owned models (Battle Reports, run-derived tables, presets, snapshots, and player-state rows).
- Kept definition/reference tables global (no player ownership fields).

### Queryset and View Enforcement

- Core views derive the current Player from `request.user` (never from a query parameter or form input).
- All data fetches for owned tables filter by `player=…` consistently.
- A regression test asserts that two authenticated users cannot see each other’s Battle History or Charts.

### Admin Behavior

- Admin querysets are filtered to the authenticated user’s Player for non-superusers.
- Admin writes assign ownership automatically for non-superusers, preventing reassignment to a different Player.

### New Invariants Introduced

- The client never supplies `player_id` in requests; player ownership is server-derived.
- Every owned table has an explicit `player` relationship.
- Owned join tables validate “single-player-only” constraints (for example, preset links and parameter rows).

## Pillar 2 — Trustable, Explainable Goal-Aware Advice

- Advice remains read-only and descriptive, with language guardrails to prevent prescriptive phrasing.
- Goal-aware comparisons reuse existing metrics but change only the weighting and presentation layer.
- Advice degrades safely when data is thin, returning “Insufficient data” rather than implying conclusions.

## Pillar 3 — Demo, Export, and Adoption Features

### Demo Mode (Read-only Exploration)

- Added a session-scoped demo mode that switches views to a seeded, shared demo dataset.
- Demo mode is clearly labeled in the UI and blocks write actions (imports, edits, and snapshot creation).
- Demo access remains scoped and does not allow selecting arbitrary players.

### Lightweight Export

- CSV export supports derived chart datasets only and remains player-scoped.
- PNG export is implemented as chart-image downloads from the rendered chart canvases, reflecting current filters and context.
- Exports are snapshots and do not create background jobs or external storage dependencies.

## Non-Goals and Deferred Work

- No new simulations or prescriptive recommendation logic.
- No shareable links or external hosting for exports.
- No multi-player “switch to another real user’s player” feature.
- No restructuring of analysis engine architecture beyond enforcing the no-Django-import rule for `analysis/`.

## Migration and Compatibility Notes

- Existing owned rows must have a valid `player` relationship after Phase 8 migrations; backfills should remain deterministic and auditable.
- Snapshot payloads are versioned and stored as JSON-safe DTOs to support replays across sessions.
- Demo mode reserves a dedicated system username and should remain unavailable for normal sign-ups to avoid collisions.


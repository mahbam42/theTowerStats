# Admin Panel

This page is **Developer Documentation**. It documents how the Django Admin is structured, scoped, and maintained.

## Purpose

The admin panel is used for:

- Curating wiki-derived reference data.
- Inspecting ingest outputs and player state.
- Maintaining patch boundary markers for chart interpretation.

## Access and permissions

- Access is limited to ` staff ` (permission group) or superusers via Django Admin.
- ` player ` group members (default for accounts created via the login page) are restricted from accessing Django Admin.
- Ownership fields are enforced in admin classes and should never be editable by non-superusers.

## Player scoping rules

Two admin modules define a `PlayerScopedAdmin` base class that enforces per-player querysets and assigns ownership on create. Any new player-owned model registered with Django Admin should inherit from the local `PlayerScopedAdmin` implementation in its app.

- `gamedata.admin.PlayerScopedAdmin`
- `player_state.admin.PlayerScopedAdmin`

## Reference data management

Reference data is maintained through admin registrations in `definitions.admin`. These entries are the source of truth for:

- Card, bot, ultimate weapon, and guardian chip definitions.
- Parameter definitions and level tables.
- Patch boundary labels used by chart flags.

When updating reference data, preserve raw values and follow the wiki immutability rules already enforced in the models.

## Common admin workflows

### Review a player run import

1. Open `Battle reports` and confirm the latest `parsed_at` timestamp.
2. Open the related `Battle report progress` row and verify `tier`, `wave`, and `real_time_seconds`.
3. `Run bots`, `Run guardians`, and `Run combat/utility ultimate weapons` exist for future ingestion but are not populated in production. Use `Battle report derived metrics` for the current source of bot/guardian/ultimate-weapon-related totals.

### Curate wiki-derived reference data

1. Open `Wiki data` and locate the relevant `canonical_name` or `entity_id`.
2. Review the linked definition entry (cards, bots, ultimate weapons, guardian chips).
3. Update parameter definitions or level rows only when the wiki source has been re-imported.

### Maintain patch boundary markers

1. Open `Patch boundaries` and add or update the `boundary_date`.
2. Add an optional label that matches the public patch identifier.
3. Verify chart flags in the dashboard after changes are saved.

### Inspect saved chart snapshots

1. Open `Chart snapshots` and filter by `player`.
2. Confirm `target` and `name` reflect the intended saved view.
3. Use this table to support bug reports or reproduce chart configurations.

## Admin module reference

### Definitions

::: definitions.admin
    options:
      show_root_heading: true
      members: true

### Game data

::: gamedata.admin
    options:
      show_root_heading: true
      members: true

### Player state

::: player_state.admin
    options:
      show_root_heading: true
      members: true

# Phase 3 — UI Structure + Model Scaffolding

This page is **Developer Documentation**. It summarizes Phase 3 deliverables and constraints for maintainers.

Phase 3 focuses on **navigation clarity** and **page-level separation of concerns** as the dataset grows.
This phase intentionally avoids new gameplay math or analysis changes.

## Global Navigation

All pages render a simple, persistent navigation bar with links to:

- Battle History
- Charts
- Cards
- Ultimate Weapon Progress
- Guardian Progress
- Bots Progress

## Pages

- **Battle History**
  - Lists imported runs (`GameData` + `RunProgress`) with minimal metadata.
- **Charts**
  - Reuses the existing chart dashboard (no new chart logic).
- **Cards**
  - Lists card definitions and player card progress (structural/placeholder data).
  - Shows preset labels for grouping.
- **Ultimate Weapon / Guardian / Bots Progress**
  - Placeholder pages for Phase 3 structure.

## Models (Structural)

Phase 3 adds schema-only models to support inspection and future work:

- Shared: `Unit`
- Cards: `CardDefinition`, `CardParameter`, `CardLevel`, `CardSlot`, `PlayerCard`
- Ultimate Weapons: `UltimateWeaponParameter`, `PlayerUltimateWeapon`
- Guardians: `GuardianChipParameter`, `PlayerGuardianChip`
- Bots: `BotParameter`, `PlayerBot`

These models are intended for traceable storage and admin/debug visibility; behavior and game mechanics are added in later phases.

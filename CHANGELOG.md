# Changelog

This project follows Semantic Versioning.

## [0.2.2] (in progress)

- Notes: Adds new charts/metrics and UI refinements.
- Cards dashboard: select multiple cards and apply presets in bulk (assign or create preset tags).
- Cards dashboard: replace placeholder descriptions with the current level value (bolded) when available (placeholders allowed at level 0).
- Cards dashboard: rename the Level column to Next Level and add a brief Presets explainer.
- Charts dashboard: add chart taxonomy domains (Economy, Damage, Enemy Destruction, Efficiency) with validation guardrails (no cross-currency cash vs coins, no cross-domain metrics except explicit comparative charts).
- Charts dashboard: add coins/cash source breakdown charts (including “Coins From Ultimate Weapons” and “Cash by Source”) and document cash as in-run purchasing power (non-persistent).
- Charts dashboard: add damage charts (damage by source, percent contribution, and comparative damage vs enemies destroyed; orb effectiveness).
- Charts dashboard: add enemy destruction charts and derive totals by summing per-type rows (ignores Battle Report “Total Enemies” and “Total Elites” due to asymmetry).
- Charts dashboard: donut charts include percent labels; comparative charts support multiple y-axes when units differ.
- Bug fix: tolerate Guardian chip upgrade table cost header drift during `rebuild_wiki_definitions`.

## [0.1.0]

- Developer documentation: [Phase 8](docs/phase8.md), [Phase 9](docs/phase9.md)
- Battle Report import with deduplication and safe handling of unknown labels
- Charts with filters, snapshots, and exports (CSV, PNG)
- Read-only progress dashboards for cards, ultimate weapons, guardian chips, and bots
- Per-account data isolation and optional demo dataset

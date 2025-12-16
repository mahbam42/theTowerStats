# theTowerStats

Welcome to the documentation hub for **theTowerStats**. Players can explore history, charts, and collection progress without editing or optimizing data.

> **Highlight — Charts**
> The Charts dashboard uses Foundation layouts with a default start date of 2025-12-09 UTC. Filters and overlays rely on existing `MetricSeries` outputs only.

> **Highlight — Cards**
> The Cards dashboard surfaces unlocked slots, preset tags, and player card progress in read-only tables.

## What’s inside

- **User Guide** — Task-based instructions for Battle History, Charts, Cards, Ultimate Weapons, Guardian Chips, and Bots.
- **Wiki Population** — How to ingest and rebuild wiki-derived data safely.
- **Development** — Previous phases, structure notes, and internal architecture for maintainers.
- **Reference** — mkdocstrings-backed pages for management commands and future public APIs.

## Principles

- Keep `analysis/` pure and Django-free.
- Keep Django apps focused on persistence and presentation.
- Preserve raw imported values without destructive transforms.

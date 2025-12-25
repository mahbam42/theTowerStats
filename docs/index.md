# theTowerStats

Welcome to the documentation hub for **theTowerStats**. Players can explore history, charts, and collection progress without changing imported Battle Report data.

Published documentation: <https://mahbam42.github.io/theTowerStats/>

> **Highlight — Charts**
> The Charts dashboard defaults to the current in-game Event window (14 days) and lets you select one or more charts, then filter by date range, granularity, tier, and preset labels.

> **Highlight — Cards**
> The Cards dashboard surfaces unlocked slots, preset tags, and player card progress in read-only tables.
> Presets define card groupings (unlocked via Lab Research “Card Presets”). The game currently allows 6 presets to be set, and this app allows as many as you’d like.
> Presets can also be assigned to Battle Reports to track card usage over time.

## What’s inside

- **User Guide** — Task-based instructions for Battle History, Charts, Cards, Ultimate Weapons, Guardian Chips, and Bots.
- **Wiki Population** — How to ingest and rebuild wiki-derived data safely.
- **Development** — Previous phases, structure notes, and internal architecture for maintainers.
- **Reference** — mkdocstrings-backed pages for management commands and future public APIs.

## Principles

- Keep `analysis/` pure and Django-free.
- Keep Django apps focused on persistence and presentation.
- Preserve raw imported values without destructive transforms.

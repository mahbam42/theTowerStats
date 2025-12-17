# Player User Guide

## Overview

Welcome to **theTowerStats** — a dashboard that turns imported Battle Reports into clear history, charts, and collection summaries. This guide focuses on how to review your imports and track progress you want to save in the app.

> **Note**
> This guide avoids strategy advice. Everything shown is factual, computed from your imports and saved progress.

## Setup

- Sign in to the app (local builds default to the bundled demo user).
- Navigate to **Battle History** to paste a Battle Report from the game when you have a new run to record.
- Optional: add a preset label while importing to keep runs grouped by your own goals.

## Operation

### Battle History

- Open **Battle History** from the top navigation.
- Use filters for **Tier**, **Killed by** text, and **Goal** (preset label) to narrow the table.
- Columns show battle date, tier, preset, and computed coins/hour. When data is missing from a report, the cell displays an em dash.
- Pagination keeps scans quick; sorting options favor recent runs by default.

> **Note**
> Battle History surfaces only what exists in your imported text. If a label never appeared in the report, it will not be synthesized here.

### Charts

- Open **Charts** to view time-series graphs from your imported runs.
- Filters default to a start date of **2025-12-09 UTC**; adjust date range, tier, preset, and moving average window as needed.
- Select one or more charts from the chart selector to control what is displayed.
- Context and filters stay visible above the charts so you can trust the scope of each graph.

> **Caution**
> Charts never perform inline math in the browser. All values come from precomputed series returned by the analysis engine.

### Cards

- Open **Cards** to see unlocked slots, preset tags, and your card table.
- Stars unlocked and last updated timestamps are shown per card; values are read-only.
- A card library grid lists all known definitions for quick reference.

### Ultimate Weapons

- Visit **Ultimate Weapons** to review unlocked status and parameter levels per weapon.
- Select **Unlock** and **Level Up** to save your Ultimate Weapon progress in the app.
- Costs are informational only; the app does not check affordability.

### Guardian Chips

- Open **Guardians** to track chip unlocks, active selection, and upgrade progress.
- You can have up to two active Guardian Chips at a time.
- Costs are informational only; the app does not check affordability.

### Bots

- Visit **Bots** to track bot unlocks and upgrade progress.
- Bots do not have an active or inactive toggle in the app.
- Costs are informational only; the app does not check affordability.

## Advanced

- Use **Comparison** on the Charts page to contrast two runs or two date windows by coins/hour.
- Overlay options let you view series grouped by tier or preset without recalculating values.
- Moving averages smooth volatile series; the underlying raw datapoints remain unchanged.

> **Warning**
> No derived values are persisted. Refreshing or changing filters always reuses existing computed series.

## Appendix

- Documentation uses Material for MkDocs with mkdocstrings for management command reference.
- Need to repopulate data from the wiki? See **Wiki Population** in the navigation for offline-safe steps.
- For developer notes and earlier project phases, open the **Development** section.

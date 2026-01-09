# The Tower – Stats & Analysis App

A stats‑tracking and analysis app for **The Tower** mobile game.

Battle history can be imported as raw text, then explored through charts and read-only progress dashboards — without guesswork or prescriptive advice.

## Links

- App (Railway): https://thetowerstats.up.railway.app/
- Docs: https://mahbam42.github.io/theTowerStats/

---

## TL;DR — Product Philosophy

**This app helps you understand your own Tower runs.**

It turns Battle Reports into history, charts, and comparisons so you can see what changed, when it changed, and under what conditions.

* No leaderboards
* No “best build” claims
* No hidden assumptions
* No telling you how to play

Everything is based on *your data*, shown with clear context and stated assumptions.
If there isn’t enough data to support a conclusion, the app says so explicitly.

**It’s a mirror, not a meta.**

Guiding principles:

* Raw Battle Reports are the source of truth
* Context defines scope, not meaning
* Trust and explainability come before cleverness

## What This App Does

### 📥 Import Battle History

- Paste raw **Battle Report** text directly from the game
- Automatic deduplication (no accidental double imports)
- Gracefully handles new or unknown stat labels after game updates
- Each signed-in account is isolated; your imports are scoped to your user.

### 📊 Track Progress Over Time

- Coins per hour and other precomputed series (no client-side math)
- Filter charts by **date range**, **tier**, **preset**, and overlays
- Default chart window uses the current **Event window**, with navigation controls
- Default chart granularity is **By battle log**, with an optional switch to **By date**
- Chart run labels follow Battle History ordering for consistent comparisons
- Export derived metrics to CSV and download chart images as PNG snapshots
- Full-screen chart modal and tooltip links to open Battle Report details
- Guided walkthrough available in demo mode or on first login

### 🎯 Goals Dashboard

- Track upgrade targets across bots, guardian chips, and ultimate weapons
- See level targets, current vs target deltas, and estimated costs

### 🧮 Analysis (Deterministic, Traceable Outputs)

- Computes rates, totals, deltas, and comparisons from your imported runs
- Keeps outputs explainable by showing the scope (filters and included runs)
- Uses descriptive language for summaries (never “best”, “optimal”, or “you should”)

### 🧩 Card, UW, Guardian, and Bot Tracking

- Read-only dashboards for cards, ultimate weapons, guardian chips, and bots
- See unlocks, parameter levels, and last-updated timestamps
- Wiki‑derived data is versioned and attributed, never overwritten

### 🗂 Presets (Player Intent, Not Strategy)

- Group cards into named presets that match **your play style**
- Use presets as filters for analysis and charts
- The app never tells you what’s “best” — it shows you what happened

### 🌙 Foundation-powered UI

- Dark theme UI with consistent tables, callouts, and navigation styling
- Improved callout and help-text contrast in dark theme
- Shared dashboard shell with top navigation, global search, and consistent callouts
- Foundation grid/forms for Battle History, Charts, and progress dashboards
- Clear charts designed to answer real questions quickly
- Optional demo dataset (early, mid, and late game samples) for safe exploration without importing your own data

---

## What This App Is *Not*

- ❌ A strategy guide
- ❌ An auto‑optimizer
- ❌ Real‑time wiki scraper

Any future advice or recommendations are explicitly out of scope unless added later.

---

## Why This Exists

The Tower exposes a huge amount of data — but very little context.

This app is about:
- remembering what you’ve tried,
- seeing how changes affect outcomes over time,
- and giving you trustworthy numbers to support your own decisions.

---

## Current Progress

- Current development: **v0.6.2**
- Latest release: **v0.6.2**
- Changelog: `CHANGELOG.md`
- Stable: Battle Report import, Battle History, Charts (including snapshots and compare scopes), and collection progress dashboards
- Multi-user: Each signed-in account has its own isolated dataset
- Adoption features: A read-only demo dataset and lightweight export tools (CSV and PNG)

See the User Guide and Development sections in `/docs` ([or the published site](https://mahbam42.github.io/theTowerStats/)) for deeper detail.

### Testing

Tests are run in CI and during development.
Production deployments install runtime dependencies only and do not execute tests.
Maintainers can preview wiki diffs before rebuilds with `rebuild_wiki_definitions --diffs`.

# The Tower – Stats & Analysis App

A stats‑tracking and analysis app for **The Tower** mobile game.

Paste your battle history, visualize your progress over time, and explore how different mechanics actually affect your runs — without guesswork or prescriptive advice.

---

## What This App Does

### 📥 Import Battle History
- Paste raw **Battle Report** text directly from the game
- Automatic deduplication (no accidental double imports)
- Gracefully handles new or unknown stat labels after game updates

### 📊 Track Progress Over Time
- Coins per hour and other precomputed series (no client-side math)
- Filter charts by **date range**, **tier**, **preset**, and overlays
- Default chart window starts on **2025-12-09 UTC** for recent-run focus

### 🧮 Analysis Engine (The Core Feature)
- Deterministic, testable calculations
- Computes:
  - rates (coins/hour, waves/minute)
  - deltas between runs
  - derived metrics (EV, effective cooldowns)
- No strategy preaching — just numbers you can interpret yourself

### 🧩 Card, UW, Guardian, and Bot Tracking
- Read-only dashboards for cards, ultimate weapons, guardian chips, and bots
- See unlocks, parameter levels, and last-updated timestamps
- Wiki‑derived data is versioned and attributed, never overwritten

### 🗂 Presets (Player Intent, Not Strategy)
- Group cards into named presets that match **your play style**
- Use presets as filters for analysis and charts
- The app never tells you what’s “best” — it shows you what happened

### 🌙 Foundation-powered UI
- Shared dashboard shell with top navigation, global search stub, and consistent callouts
- Foundation grid/forms for Battle History, Charts, and progress dashboards
- Clear charts designed to answer real questions quickly

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

## Project Status

🚧 **Phase 5 in progress**

- UI refit with Foundation across all dashboards
- Read-only progress pages for cards, ultimate weapons, guardians, and bots
- Player-facing documentation published via MkDocs Material

See the User Guide and Development sections in `/docs` (or the published site) for deeper detail.

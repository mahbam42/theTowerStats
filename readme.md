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
- Coins per hour, waves reached, damage output, and more
- Filter charts by **date range** and **tier**
- Designed for fast visual feedback, not spreadsheets

### 🧮 Analysis Engine (The Core Feature)
- Deterministic, testable calculations
- Computes:
  - rates (coins/hour, waves/minute)
  - deltas between runs
  - derived metrics (EV, effective cooldowns)
- No strategy preaching — just numbers you can interpret yourself

### 🧩 Card, UW, Guardian, and Bot Tracking
- Log your collection and unlock progress
- See how upgrades evolve over time
- Wiki‑derived data is versioned and attributed, never overwritten

### 🗂 Presets (Player Intent, Not Strategy)
- Group cards into named presets that match **your play style**
- Use presets as filters for analysis and charts
- The app never tells you what’s “best” — it shows you what happened

### 🌙 Clean, Focused UI
- Dark‑mode by default
- Mobile‑friendly battle report input
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

🚧 **In active development**

The app is being built in clearly scoped phases:
1. End‑to‑end ingestion and charting
2. Contextual filtering and comparisons
3. Parameterized effects and derived metrics

See the planning documents in `/docs` for deeper technical detail.


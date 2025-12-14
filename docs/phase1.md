# Phase 1: Battle Report → Chart

Phase 1 proves the end-to-end pipeline works:

1. paste a Battle Report (raw text),
2. store it safely with dedupe,
3. analyze it via the Analysis Engine,
4. render a simple time-series chart.

## UI

- Dashboard: `/`
  - Paste/import form (POST)
  - Date range filter (GET `start_date`, `end_date`)
  - Chart: **coins per hour** over time

## Data Stored

- `core.models.GameData`
  - raw Battle Report text is preserved unchanged
  - deduplicated via a SHA-256 checksum
- `core.models.RunProgress`
  - stores only Phase 1 metadata: battle date, tier, wave, real time
  - accepts labels separated by colons, tabs, or multi-space alignment
  - tolerates missing/reordered sections and unknown labels (non-fatal)
  - Battle Dates may use ISO, numeric, or month-name formats (e.g. `Dec 07, 2025 21:59`)
  - parses real-game tab-delimited reports (e.g. `Battle Date\tDec 14, 2025 01:39`)

## Analysis Engine

- Entry point: `analysis.engine.analyze_runs`
- Input: iterable of `RunProgress`-like objects (duck-typed)
- Output: DTOs in `analysis.dto` (no database writes)
  - Coins are parsed best-effort from raw text via `analysis.quantity` (e.g. `Coins: 4.24M`).
  - Missing required fields are skipped so empty inputs return an empty result instead of errors.

## Limitations (By Design)

- Only extracts **Battle Date**, **Tier**, **Wave**, **Real Time**
- Ignores all other labels (unknown labels are non-fatal)
- Computes only one metric: **coins per hour**

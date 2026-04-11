# Changelog

This project follows Semantic Versioning.

## [0.13.0]

### Added
- Battle Report ingestion for the newer v28 section-based stat layout while keeping compatibility with older imported reports.
- New chartable and explorable metrics for game-reported `Coins/hour`, game-reported `Cells/hour`, record rows, blocked-damage families, new currency rows, damage taken, enemy level skips, and newer Battle Report count metrics.
- Lifetime Stats Records rows for Highest Coins / Minute, Largest Wave Skip, Most Coins From Wave Skip, Most Cells From Wave Skip, Largest Smart Missile Stack, Largest Golden Combo, Most Coins From Golden Combo, and Largest Inner Landmine Charge.
- Charts source-breakdown controls for switching donut panels to ranked horizontal bar views.
- Full-screen chart modal support for showing a data table built from the active chart payload.
- Additional card-usage observed metrics for Energy Shield hits absorbed, Nuke uses, Second Wind uses, Demon Mode uses, Coins from Critical Coin, and Death Ray Damage.

### Changed
- Metric labeling now distinguishes app-derived per-hour values from game-reported per-hour values.
- Battle Report parsing now accepts day-based run durations when newer reports include `d` in the Game Time value.
- Metrics Reference, Charts, Battle History, and Lifetime Stats documentation now describe the newer Battle Report layout and record-style metrics.
- Lifetime Stats now groups Highest Coins / Minute with Recent Coins per Hour, keeps newer combat records under Combat, and places wave-skip and smart-missile stack records under Utility.
- Built-in charts now include newer source metrics and dedicated currency charts for Gems Earned, Ad Gems Earned, and Medals Earned.
- Source-breakdown chart panels now place Show data table and Download PNG above the display-mode controls, and long horizontal bar views scroll within the panel instead of growing indefinitely.
- Developer and user documentation now cover the newer chart controls, source metrics, reparse guidance, and manual QA coverage for v28 chart behavior.

### Fixed
- Raw metric extraction now resolves section-scoped labels in newer Battle Reports without breaking older label formats.
- Large compact-number parsing now accepts newer suffixes used by the game, including `s`, `S`, `o`, and `O`.
- Legacy Black Hole damage extraction now tolerates the historical `Blackhole Damage` label variant.
- Battle Report validation no longer rejects valid v28 reports when section labels or newer `Wave ...` rows appear in the pasted text.
- Raw metric extraction now tolerates single-space v28 clipboard pastes for section-scoped metrics and source breakdown rows.
- Charts can backfill missing raw-text-derived metrics from stored Battle Report text when older imports predate newer parser support.
- Source-breakdown donuts now show tiny non-zero slices as `<0.1%` instead of `0.0%`.
- Frontend chart formatting now preserves higher-order compact suffixes such as `s`, `S`, `o`, and `O` instead of collapsing them into lower-order suffixes.

## [0.12.0]

### Added
- Cards dashboard usage modal with sortable card and preset usage tables based on visible Battle Report preset tags.
- Shared account-menu link to open the GitHub bug report / feature request chooser.

### Changed
- Bot Respec now performs a destructive in-app reset that locks tracked bots, resets bot parameter levels to 0, and clears bot goals after the in-game respec is recorded.
- Explore Query Templates now collapse after a successful query run and remain open when validation errors are present.
- Dependencies updated across runtime and development tooling, including refreshed constraints and lockfile entries for `dj-database-url`, `gunicorn`, `psycopg`, `whitenoise`, `requests`, `ruff`, `mkdocs-material`, `mkdocs-gen-files`, `mkdocs-get-deps`, `pymdown-extensions`, and `mkdocstrings-python`.
- Local virtual environment and lockfile now align with Django 5.2.12 and Requests 2.33.0.

### Fixed
- `fetch_wiki_data` now validates parsed Fandom hostnames instead of relying on substring suffix checks for the MediaWiki parse-API fallback.

## [0.11.0]

### Added
- Explore query templates backed by database storage, including Admin-managed built-in templates for Farming Efficiency by Tier, Guardian Chip Performance, and Reroll Shards Earned.
- Battle History rank filtering for the Top 3 Tournament Logs summary widget.
- Bot Respec event-window tracking so usage is recorded per event window instead of as a timeless lock.

### Changed
- Dependencies updated across runtime and development tooling, including Django 5.2.12 and aligned package/version files.
- Explore template records remain editable through Django Admin and are copied into the editor without auto-running.
- Local staging database refresh now reapplies Django migrations against the restored local database after `pg_restore`.

### Fixed
- Coins Earned by Source now includes `guardian_coins_stolen` in the chart breakdown.
- Bot Respec stays disabled only for the current event window and becomes available again when the next event window starts.

## [0.10.1]

### Changed
- Guardian chip rebuild recognizes Scout chip parameter ordering (Cooldown, Range Bonus, Duration).
- Dependency management now includes a Pipfile lockfile and Dependabot updates for Python requirements.
- Dependencies: bump Gunicorn to 25.x and pytest to 9.x.
- Deploy pipeline: wiki rebuild supports offline mode and an optional timeout via `TOWERSTATS_WIKI_REBUILD_TIMEOUT_SECONDS`.

### Fixed
- `fetch_wiki_data` falls back to the Fandom MediaWiki parse API when direct page fetches return 403/429.
- Bump Django minimum version to 5.2.11 to address upstream security advisories.
- Deploy pipeline no longer aborts when wiki rebuild fails; it logs the failure and continues.

## [0.10.0]

### Added
- Lifetime Stats modal with economy, combat, and utility totals plus date range filters.
- Calculator Tools dashboard with Game Speed and Labs Speed Up calculators.
- Explore per-hour metrics for cells, reroll shards, enemies destroyed, waves, and run duration hours.
- Explore sum and average aggregations for Guardian Damage metrics.
- Staging database refresh script for pruning production snapshots to a single player.

### Changed
- Guardian chip rebuild recognizes Scout chip parameter ordering (Cooldown, Range Bonus, Duration).
- Compare and Advice now open in modals on the Charts dashboard.
- Game Speed calculator now uses the Wave Accelerator card level for timing adjustments.
- Labs Speed Up calculator deadlines use UTC midnight at the end of the current Event window.
- Local tests default to SQLite; test database override options are documented.
- Postgres version aligned with production; local DB URL updated.
- Battle Report progress now stores parsed Game Time seconds for hour-based metrics.
- Docs: update roadmap and docs theme toggle notes.

### Fixed
- Explore Game Time parsing for hour-bucket queries.
- Explore Farming Efficiency deltas and cells display.
- Explore saved queries now preserve comments and load reliably.
- Charts context highlighting and Compare modal behavior.
- Player admin display and last_login timestamps.
- Game Speed calculator form binding.

## [0.9.0]

### Added
- Patch boundary filters for Charts and Explore scopes, including Compare shortcuts for patch windows.
- Guardian Chip slot unlock tracking for slots 2 (200 Bits) and 3 (300 Bits), with support for up to three active chips.
- Explore DSL support for patch boundary filters.

### Changed
- Metrics Reference now lists the Explore DSL key for each metric.
- Guardian Chips dashboard surfaces active slot counts and unlock costs.

### Fixed
- Explore multi-metric tables now show a single Runs counted column with mismatch markers.
- Cards dashboard default sort now orders by rarity.
- dd Explore DSL alias for run duration. 

## [0.8.3]

### Added
- Metrics Reference page linked from Chart Builder and Explore.
- Explore breakdowns user guide reference page.
- Developer documentation for the Explore registry.

### Changed
- Battle Report import preset selection now uses a dropdown with a create-new option.

### Fixed
- Free Upgrades by Run tooltip totals now sum attack, defense, and utility upgrades.
- Battle History sorting now includes Tournament and Recovery packages columns.
- Goals modal candidate list text now uses readable contrast on dark backgrounds.

## [0.8.2]

### Fixed
- Explore DSL parsing no longer uses backtracking-prone patterns for scope/filter parsing.
- Explore DSL date ranges now reject malformed separators.
- Explore DSL metric alias support for `enemies_destroyed_elites` in validation/autocomplete.
- Explore DSL editor autocomplete now refreshes stale cache entries missing metrics.
- CodeMirror style expansion now replaces all `&` placeholders.
- CodeMirror special character ranges now use explicit hex escapes.

## [0.8.1]

### Added
- Explore dashboard with query schema, query registry, DSL editor, and Query Explorer modal preview.
- Explore results link back to runs from the Query Explorer modal preview.
- Explore DSL support for preset name include/exclude, wildcards, all/* selectors, and enemy group metrics.
- Explore DSL support for avg aggregation, multi-metric outputs, percent-of-total metrics, and a built-in Farming Efficiency by Tier query with summaries and warnings.
- Explore DSL editor autocomplete backed by server query metadata.
- Battle History column for Recovery Packages (hidden by default via Columns).
- Charts context control to exclude multiple presets.
- UW Sync chart toggles to show/hide Death Wave and Golden Bot activation markers.

### Changed
- Explore results rendering to always show the table, with optional chart outputs, legends, totals, and theme palette styling.
- Explore Farming Efficiency summary now includes secondary metrics.
- Explore DSL docs moved to reference, and docs navigation reorganized for project links and ordering.
- API docs now list current JSON endpoints.
- Roadmap documentation updated.
- Docs note that imported Battle Logs use UTC timestamps.

### Fixed
- Bot rebuilds now preserve configured Level 0 bot parameter rows.
- Explore DSL metric parsing and breakdown separators.
- Explore DSL editor bundling to eliminate CodeMirror state mismatch.

## [0.7.1]

- Charts: add tournament rank filters, tournament scopes in Compare, and combined tier/tournament context selection.
- Charts: add snapshot filters and past-N-runs context filters that combine with date ranges.
- Charts: add ordered favorites and saved Chart Builder entries editable in the modal.
- Battle History: require tournament rank on new imports and show tournament rank badges.
- UI: standardize unit formatting in Compare, Battle History coins/hour, and Battle Report modal metrics.
- Ops: add a Railway deploy command that runs migrations, wiki rebuild, and Battle Report reparse.
- MOTD: show a one-time banner on deploy and surface the latest changelog summary on Getting Started.
- Docs: update Charts, Compare, Battle History, Chart Builder, and user guide for new filters and preferences.
- ci: consolidate test/stability updates for deployment readiness and environment parity.

## [0.6.2]

- Battle History: show coins per real hour in the table and modal when reported.
- Battle History: fall back to import timestamps for missing battle dates and label imported dates in the UI.
- Battle History modal: use player-scoped run numbers.
- Charts: add tier/preset compare selectors, scope averaging toggle, and scope size warnings.
- Bots: mute Amplify Bot runs used; infer bot runs used from Battle Report bot metrics.
- Guardian Chips: infer runs used for trackable chips from Battle Report metrics; mute Ally runs used.
- Commands: extend `reparse_battle_reports` to backfill bot usage, support patch windows, and reapply battle date fallback.
- Docs: update compare, battle history, battle report modal, bots, guardian chips, goals, and management command guidance.

## [0.6.1]

- Bots: normalize rebuild headers (including non-breaking spaces) and accept level 0 rows when present.
- Bots: populate Runs used from battle report bot lines.
- Guardians: remove unexpected parameter definitions during rebuild to prevent dashboard skips.
- Ultimate Weapons: map generic cost headers (Cost, Cost__2, Cost__3) during rebuilds.
- Cards: normalize effect headers when deriving card effects.
- Docs: note header normalization for wiki rebuilds and clarify bot runs usage.

## [0.6.0]

- Charts: fix run numbering so chart labels match Battle History ordering.
- Charts: abbreviate large values in axes and tooltips using compact suffixes.
- Cards: show correct level 0 values in the card library.
- Bots: fix baseline totals in progress dashboards.
- UI: improve dark-theme styling for callouts and help text.
- Tooling: add `rebuild_wiki_definitions --diffs` preview for wiki changes.
- Docs: align preset labels, cite wiki sources, and fix formatting.
- Ops: add Google Analytics tag.
- Roadmap: update phase planning notes.

## [0.5.1] 

- UI: add dark theme styling across dashboards, navigation, tables, and callouts.
- UI: reorder dashboard layouts on mobile so main content loads first, with compact tables on small screens.
- Charts: default granularity to By battle log and reorganize dashboard controls with chart descriptions/tooltips.
- Charts: move “Include tournaments” into the primary context controls.
- Charts: compare run selectors display tier, wave, date, and time.
- Charts: add fullscreen chart modal and Battle Report modal links from chart tooltips.
- Charts: add run duration vs coins earned scatter and coins earned over time area charts.
- Charts: add free upgrades stacked chart; show total upgrades in the tooltip.
- Charts: add guided walkthrough entry point for demo mode and first login.
- Tests: expand chart builder coverage and align demo CSV export test expectations.
- Fix per-run label rendering and flagging; clarify chart labels in docs
- Docs: add Admin Panel documentation.
- Docs: add master prompts 41 and 42 to archive.
- Docs: revise Charts user guide and update development workflow notes.
- Landing page: make Getting Started the default homepage with a demo chart preview and docs links.
- Demo data: refresh sample Battle Reports with early, mid, and late-game runs.
- Roadmap: update phase planning notes.

## [0.4.0]

- Notes: Summary of the most recent development work.
- Getting started: add a landing page to explain scope and how to begin using the app.
- Charts: add scope explainers and support multi-run Compare views with summary-focused outputs.
- Charts: handle missing Battle Date by falling back to import timestamp for charting.
- Analysis: persist Battle Report derived metrics to support residual coin/cash charts and consistent chart series.
- Ops: require an explicit target for `sync_player_state` to reduce accidental cross-scope updates.
- Battle History: move coins/hour sorting into analysis and tighten player-scoped parameter updates.
- Bug fix: tolerate Guardian chip rebuild failures caused by JSON key reordering.
- Docs: add product philosophy and developer design principles pages; expand user guide chart explanations.
- Tests: add coverage for getting started, navigation, sync command behavior, and derived-metrics persistence.

## [0.3.0]

- Notes: Adds new dashboards, charts/metrics, and documentation updates.
- Cards dashboard: select multiple cards and apply presets in bulk (assign or create preset tags).
- Cards dashboard: replace placeholder descriptions with the current level value (bolded) when available (placeholders allowed at level 0).
- Cards dashboard: rename the Level column to Next Level and add a brief Presets explainer.
- Charts dashboard: add chart taxonomy domains (Economy, Damage, Enemy Destruction, Efficiency) with validation guardrails (no cross-currency cash vs coins, no cross-domain metrics except explicit comparative charts).
- Charts dashboard: add coins/cash source breakdown charts (including “Coins From Ultimate Weapons” and “Cash by Source”) and document cash as in-run purchasing power (non-persistent).
- Charts dashboard: add damage charts (damage by source, percent contribution, and comparative damage vs enemies destroyed; orb effectiveness).
- Charts dashboard: add enemy destruction charts and derive totals by summing per-type rows (ignores Battle Report “Total Enemies” and “Total Elites” due to asymmetry).
- Charts dashboard: donut charts include percent labels; comparative charts support multiple y-axes when units differ.
- Charts dashboard: default chart window to the current Event window and add Event window navigation controls.
- Charts dashboard: add per-run chart granularity toggle.
- Charts dashboard: add stacked and bar chart variants for damage breakdowns.
- Goals dashboard: add goal targets dashboard and goal widgets for upgradeable entities, including cost and delta calculations.
- Battle Report import: add manual tournament toggle to tag runs when the copied text does not indicate a tournament round.
- Developer docs: add mkdocstrings pages for analysis, charting, and parsers.
- Bug fix: tolerate Guardian chip upgrade table cost header drift during `rebuild_wiki_definitions`.

## [0.2.2]

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

- Developer documentation: Phase 8, Phase 9
- Battle Report import with deduplication and safe handling of unknown labels
- Charts with filters, snapshots, and exports (CSV, PNG)
- Read-only progress dashboards for cards, ultimate weapons, guardian chips, and bots
- Per-account data isolation and optional demo dataset

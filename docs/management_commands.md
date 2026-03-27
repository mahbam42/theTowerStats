# Management Commands

> **Note**
> Commands are intended for maintainers. They read and write database state and should be run in controlled environments.

## Wiki ingestion and rebuild

### `fetch_wiki_data`

> ⚠️ Note
> `fetch_wiki_data` only accepts true `fandom.com` hosts for the MediaWiki parse-API fallback. Crafted hosts that merely contain `fandom.com` as a substring are rejected.

::: core.management.commands.fetch_wiki_data

### `rebuild_wiki_definitions`

::: core.management.commands.rebuild_wiki_definitions

### `purge_wiki_definitions`

::: core.management.commands.purge_wiki_definitions

### `sync_player_state`

::: core.management.commands.sync_player_state

> ⚠️ Note
> `sync_player_state --player` refers to a username (the owning account), not a standalone Player name.
> The command requires either `--player` or `--all` plus an explicit `--check` or `--write`.

## Battle report maintenance

### `reparse_battle_reports`

Reparse is idempotent and supports scoped backfills.

- `--limit` processes the most recent N reports (highest ids) after any other filters.
- `--patch` limits processing to the patch window that starts at the selected PatchBoundary date and ends at the next boundary date (exclusive). Provide a boundary label or ISO date.
- Reparse also backfills bot usage rows used by **Runs used** on the Bots dashboard.

::: core.management.commands.reparse_battle_reports

## Deployment helpers

### `deploy_railway`

Runs the deploy-time pipeline (migrations, wiki rebuild, reparse).

- Requires `--write` to run.
- `--skip-migrations` skips `migrate`.
- `--skip-wiki` skips `rebuild_wiki_definitions --target all --write`.
- `--skip-reparse` skips `reparse_battle_reports --write`.
- `TOWERSTATS_WIKI_OFFLINE=1` forces `rebuild_wiki_definitions --skip-fetch` (no network fetch).
- `TOWERSTATS_WIKI_REBUILD_TIMEOUT_SECONDS` caps wiki rebuild runtime (default 300 seconds, set to 0 to disable). When exceeded, the rebuild is skipped and deploy continues.
- Wiki rebuild failures are logged and do not abort the deploy pipeline.

::: core.management.commands.deploy_railway

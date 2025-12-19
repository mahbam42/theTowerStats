# Management Commands

> **Note**
> Commands are intended for maintainers. They read and write database state and should be run in controlled environments.

## Wiki ingestion and rebuild

### `fetch_wiki_data`

::: core.management.commands.fetch_wiki_data

### `rebuild_wiki_definitions`

::: core.management.commands.rebuild_wiki_definitions

### `purge_wiki_definitions`

::: core.management.commands.purge_wiki_definitions

### `sync_player_state`

::: core.management.commands.sync_player_state

> ⚠️ Note
> `sync_player_state --player` refers to a username (the owning account), not a standalone Player name.

## Battle report maintenance

### `reparse_battle_reports`

::: core.management.commands.reparse_battle_reports

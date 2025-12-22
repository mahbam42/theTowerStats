# Wiki Population (Offline Safe)

Populate wiki-derived data in two steps: ingest raw tables, then rebuild structured definitions and player state rows.

> **Warning**
> These steps are for maintainers. They write to the database and expect stable network access only during ingestion.

## Step 1 — Ingest wiki rows

Use `fetch_wiki_data` to capture raw tables into `definitions.WikiData`. Pick the target that matches the section you need.

- All targets: `python manage.py fetch_wiki_data --target all --write`
- Slots table: `python manage.py fetch_wiki_data --target slots --write`
- Card list tables: `python manage.py fetch_wiki_data --target cards_list --write`
- Bots: `python manage.py fetch_wiki_data --target bots --write`
- Guardian chips: `python manage.py fetch_wiki_data --target guardian_chips --write`
- Ultimate weapons: `python manage.py fetch_wiki_data --target ultimate_weapons --write`

> **Note**
> Use `--check` for a dry run when validating selectors or table indexes.

## Step 2 — Rebuild definitions

Translate stored wiki rows into structured definitions without re-downloading pages:

- Dry run: `python manage.py rebuild_wiki_definitions --skip-fetch --check`
- Apply changes: `python manage.py rebuild_wiki_definitions --skip-fetch --write`

Targets (`--target`): `cards`, `bots`, `guardians`, `ultimate_weapons`, or `all` (default).

> **Note**
> When running `rebuild_wiki_definitions` with fetching enabled, the cards fetch step also ingests the slots table so card slot limits can update.

## Step 3 — Sync player state

Create or refresh Player State rows so dashboards can display ownership:

- Apply: `python manage.py sync_player_state --write`

## Optional — Purge structured tables

For refactors where you need to rebuild definitions from scratch while keeping `WikiData` intact:

- Dry run: `python manage.py purge_wiki_definitions --check`
- Apply: `python manage.py purge_wiki_definitions --force`

## Traceability rules

- `source_wikidata` points to the exact `WikiData` revision used to build the row.
- Raw values are copied as strings (no interpretation or destructive transforms).

> **Caution**
> Cooldown and duration values are sourced from external wiki tables and are treated as reference data. The wiki can be inaccurate or drift over time.

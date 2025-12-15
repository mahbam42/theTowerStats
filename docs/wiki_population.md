# Wiki Rebuild (WikiData → Definitions → Player State)

After running wiki ingestion (`definitions.WikiData`), you can rebuild the
structured Definitions layer and then synchronize Player State rows, while
preserving traceability to the exact wiki revision used.

This step is intentionally **offline** (no network access): it reads only from
the local `definitions.WikiData` table.

## Prerequisite: Ingest WikiData

Populate is a translation step only. If `definitions.WikiData` is empty (or missing a
target’s `parse_version`), population will report no changes.

Ingest the relevant wiki tables first:

```bash
python manage.py fetch_wiki_data --target slots --write
python manage.py fetch_wiki_data --target cards_list --write
python manage.py fetch_wiki_data --target bots --write
python manage.py fetch_wiki_data --target guardian_chips --write
python manage.py fetch_wiki_data --target ultimate_weapons --write
```

## Commands

### Rebuild Definitions

```bash
python manage.py rebuild_wiki_definitions --skip-fetch --check
```

Apply changes:

```bash
python manage.py rebuild_wiki_definitions --skip-fetch --write
```

Targets (`--target`):

- `cards`
- `bots`
- `guardians`
- `ultimate_weapons`
- `all` (default)

By default, `rebuild_wiki_definitions` also performs ingestion (network) by
invoking `fetch_wiki_data`. Use `--skip-fetch` to run fully offline.

### Sync Player State

After rebuilding definitions, ensure Player State rows exist for every known
definition and are linked by slug:

```bash
python manage.py sync_player_state --write
```

### Purge (Development Refactors)

To delete only structured definition + parameter tables (WikiData is retained):

```bash
python manage.py purge_wiki_definitions --check
python manage.py purge_wiki_definitions --force
```

## Traceability rules

- `source_wikidata` points to the exact `WikiData` revision used to build the row.
- Raw values are copied as strings (no interpretation or destructive transforms).

# Phase 2.75: Wiki Ingestion (Versioned, No Math)

Phase 2.75 introduces a reliable ingestion pipeline for wiki-derived data.

Scope is intentionally limited to data capture and change detection:

- fetch selected entity tables from wiki pages (cards, bots, guardian chips, ultimate weapons),
- store raw values as strings (whitespace-normalized only),
- detect changes via deterministic hashing,
- version changes without overwriting prior records.

This phase **does not** feed wiki data into the Analysis Engine or charts.

## Data model

Wiki-derived rows are stored in `definitions.models.WikiData` as versioned records:

- `entity_id` is a stable internal key (derived from the canonical name).
- `content_hash` identifies the exact row payload (`raw_row`).
- when content changes, a new row is inserted; prior rows are retained.
- `last_seen` updates when unchanged content is observed again.
- entities missing from the latest scrape are marked `deprecated=True` (never deleted).

## Management command

Fetch and diff the configured wiki table(s):

```bash
python manage.py fetch_wiki_data --check
```

Fetch the three card-list tables under `#List_of_Cards`:

```bash
python manage.py fetch_wiki_data --target cards_list --check
```

Fetch bots, guardian chips, and ultimate weapons:

```bash
python manage.py fetch_wiki_data --target bots --check
python manage.py fetch_wiki_data --target guardian_chips --check
python manage.py fetch_wiki_data --target ultimate_weapons --check
```

Persist changes to the database:

```bash
python manage.py fetch_wiki_data --write
```

Useful options:

- `--url`: override the page URL (defaults depend on `--target`)
- `--target`: `slots`, `cards_list`, `bots`, `guardian_chips`, or `ultimate_weapons`
- `--table-index`: choose table indexes explicitly (repeatable)
- `--check`: dry-run (no DB writes)
- `--write`: apply changes (required to persist)

Notes:

- For `--target cards_list`, each ingested row includes `_wiki_table_label` in `raw_row` to preserve which table it came from (e.g., rarity headings).
- Some wiki tables repeat column names (ex: multiple “Bits” or “Stones” columns); ingestion suffixes duplicates with `__2`, `__3`, ... to avoid data loss.
- Ingestion skips non-entity rows such as table "Total" summary rows and rows that are effectively empty placeholders (empty/`-`/`null`).
- For leveled upgrade tables, ingestion also skips rows where all *parameter value* cells are placeholders (even if Level/cost columns are present).
- During `rebuild_wiki_definitions`, placeholder/total leveled rows are also ignored when creating parameter level tables (UWs/Guardians/Bots).

## Next step (optional): Populate Phase 3 models

Once `definitions.WikiData` has been populated, you can rebuild the structured
Definitions layer for browsing/admin/debug visibility:

```bash
python manage.py rebuild_wiki_definitions --check
python manage.py rebuild_wiki_definitions --write
```

This step still does **not** add gameplay math or derived analysis; it simply
materializes structured rows with `source_wikidata` pointers for traceability.

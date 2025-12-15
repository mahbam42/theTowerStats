# Phase 2.75: Wiki Ingestion (Versioned, No Math)

Phase 2.75 introduces a reliable ingestion pipeline for wiki-derived data.

Scope is intentionally limited to data capture and change detection:

- fetch one entity type from one page (Cards),
- store raw values as strings (whitespace-normalized only),
- detect changes via deterministic hashing,
- version changes without overwriting prior records.

This phase **does not** feed wiki data into the Analysis Engine or charts.

## Data model

Wiki-derived rows are stored in `core.models.WikiData` as versioned records:

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

Persist changes to the database:

```bash
python manage.py fetch_wiki_data --write
```

Useful options:

- `--url`: override the page URL (defaults to the Cards page)
- `--target`: `slots` (top table) or `cards_list` (tables under `#List_of_Cards`)
- `--table-index`: choose table indexes explicitly (repeatable)
- `--check`: dry-run (no DB writes)
- `--write`: apply changes (required to persist)

Notes:

- For `--target cards_list`, each ingested row includes `_wiki_table_label` in `raw_row` to preserve which table it came from (e.g., rarity headings).

## Next step (optional): Populate Phase 3 models

Once `core.WikiData` has been populated, you can translate those revisions into
Phase 3 structural models for browsing in admin/debug pages:

```bash
python3 manage.py populate_cards_from_wiki --check
python3 manage.py populate_cards_from_wiki --write
```

This step still does **not** add gameplay math or derived analysis; it simply
materializes structured rows with `source_wikidata` pointers for traceability.

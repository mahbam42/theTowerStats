# Phase 2.75: Wiki Ingestion (Versioned, No Math)

Phase 2.75 introduces a reliable ingestion pipeline for wiki-derived data.

Scope is intentionally limited to data capture and change detection:

- fetch a single wiki table (one entity type),
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

Fetch and diff the configured wiki table:

```bash
python manage.py fetch_wiki_data --check
```

Persist changes to the database:

```bash
python manage.py fetch_wiki_data --write
```

Useful options:

- `--url`: override the page URL (defaults to the Cards page)
- `--table-index`: choose which HTML table to scrape
- `--check`: dry-run (no DB writes)
- `--write`: apply changes (required to persist)


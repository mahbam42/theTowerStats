# Wiki Population (WikiData → Structured Models)

After running wiki ingestion (`core.WikiData`), you can populate Phase 3
structural models for browsing/admin/debug visibility while preserving full
traceability to the exact wiki revision used.

This step is intentionally **offline** (no network access): it reads only from
the local `core.WikiData` table.

## Command

Dry-run (no database writes):

```bash
python3 manage.py populate_cards_from_wiki --check
```

Apply changes:

```bash
python3 manage.py populate_cards_from_wiki --write
```

Targets:

- `--target slots`: populate `CardSlot` from the wiki “Card Slots” table
- `--target cards`: populate `CardDefinition` and `CardParameter` from card list tables
- `--target levels`: populate `CardLevel` (currently a no-op until level tables are ingested)
- `--target all`: run all of the above (default)

Slot-table detection:

- The populator recognizes common header variants, including `Slot`/`Slots` and `Gem Cost`/`Cost`.

## Traceability rules

- `CardSlot.source_wikidata` and `CardParameter.source_wikidata` always point to
  the exact `WikiData` revision used to create the row.
- Raw values are copied as strings (no interpretation or destructive transforms).

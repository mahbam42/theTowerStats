"""Regression tests for guardian chip rebuild behavior.

These tests ensure rebuild code does not depend on `WikiData.raw_row` dict key
ordering, which is not preserved by JSONB backends in production.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from core.wiki_ingestion import compute_content_hash, ingest_wiki_rows, make_entity_id, scrape_leveled_entity_rows
from definitions.models import GuardianChipDefinition, ParameterKey
from definitions.wiki_rebuild import rebuild_guardian_chips_from_wikidata

pytestmark = pytest.mark.integration

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _read_fixture(name: str) -> str:
    """Read a fixture file from tests/fixtures."""

    return (FIXTURES_DIR / name).read_text(encoding="utf-8", errors="ignore")


def _sort_raw_row_keys(raw_row: dict[str, str]) -> dict[str, str]:
    """Return a copy of raw_row with keys sorted deterministically."""

    return dict(sorted(raw_row.items(), key=lambda kv: kv[0]))


@pytest.mark.django_db
def test_rebuild_guardian_chips_is_order_independent_for_json_keys() -> None:
    """Guardian chip rebuild pairs value/cost columns without dict ordering."""

    html = _read_fixture("wiki_guardian_page_v1.html")
    name = "Ally"
    entity_id = make_entity_id(name)
    scraped = scrape_leveled_entity_rows(
        html,
        table_index=2,
        entity_name=name,
        entity_id=entity_id,
        entity_field="Guardian",
        add_level_if_missing=True,
        header_aliases={
            "Cooldown (s)": "Cooldown",
            "Cooldown(s)": "Cooldown",
            "Max Recovey": "Max Recovery",
            "Max Recovery": "Max Recovery",
        },
    )
    sorted_scraped = [
        replace(
            row,
            raw_row=_sort_raw_row_keys(row.raw_row),
            content_hash=compute_content_hash(_sort_raw_row_keys(row.raw_row)),
        )
        for row in scraped
    ]
    ingest_wiki_rows(
        sorted_scraped,
        page_url="https://example.test/wiki/Guardian",
        source_section=f"guardian_chips_{entity_id}_table_2",
        parse_version="guardian_chips_v1",
        write=True,
    )

    rebuild_guardian_chips_from_wikidata(write=True)

    chip = GuardianChipDefinition.objects.get(slug=entity_id)
    assert chip.parameter_definitions.count() == 3
    assert set(chip.parameter_definitions.values_list("key", flat=True)) == {
        ParameterKey.RECOVERY_AMOUNT.value,
        ParameterKey.COOLDOWN.value,
        ParameterKey.MAX_RECOVERY.value,
    }


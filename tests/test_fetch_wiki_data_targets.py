"""Unit tests for fetch_wiki_data target resolution and table selection."""

from __future__ import annotations

import pytest
from django.core.management.base import CommandError

from core.management.commands import fetch_wiki_data

pytestmark = pytest.mark.unit


def test_iter_ingestion_specs_target_all_builds_all_targets(monkeypatch) -> None:
    """The all target expands to every supported target using default URLs."""

    monkeypatch.setattr(fetch_wiki_data.Command, "BOT_PAGES", (("Test Bot", "https://example.test/Bot#Cost"),))
    monkeypatch.setattr(
        fetch_wiki_data.Command,
        "UW_PAGES",
        (("Test UW", "https://example.test/UW"),),
    )

    def fake_fetch_html(_url: str) -> str:
        return (
            '<span class="mw-headline" id="Ally_Chip"></span>'
            '<span class="mw-headline" id="Boss_Chip"></span>'
        )

    monkeypatch.setattr(fetch_wiki_data, "_fetch_html", fake_fetch_html)

    specs = fetch_wiki_data._iter_ingestion_specs(target="all", url_override=None)
    targets = {spec.target for _, spec in specs}
    assert targets == {"slots", "cards_list", "bots", "guardian_chips", "ultimate_weapons"}


def test_iter_ingestion_specs_target_all_rejects_url_override() -> None:
    """The all target rejects `--url` because multiple targets would be ambiguous."""

    with pytest.raises(CommandError):
        fetch_wiki_data._iter_ingestion_specs(target="all", url_override="https://example.test/wiki")


def test_resolve_table_indexes_slots_prefers_slots_table_over_leading_tables() -> None:
    """Slots selection prefers the table with Slots + a cost column."""

    html = (
        "<table>"
        "<tr><th>Other</th></tr>"
        "<tr><td>1</td></tr>"
        "</table>"
        "<table>"
        "<tr><th>Slots</th><th>Gem Cost</th></tr>"
        "<tr><td>22</td><td>1000</td></tr>"
        "</table>"
    )
    spec = fetch_wiki_data._IngestionSpec(
        target="slots",
        kind="slots",
        parse_version="cards_v1",
        source_prefix="cards_table",
    )
    assert fetch_wiki_data._resolve_table_indexes(html, target="slots", explicit_indexes=None, spec=spec) == [1]


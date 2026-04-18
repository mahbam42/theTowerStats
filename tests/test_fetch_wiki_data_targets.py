"""Unit tests for fetch_wiki_data target resolution and table selection."""

from __future__ import annotations

import pytest
import urllib.error
from http.client import HTTPMessage
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


@pytest.mark.regression
def test_iter_ingestion_specs_bots_includes_bot_bot_page() -> None:
    """Default bot ingestion specs should include the Bot Bot cost page."""

    specs = fetch_wiki_data._iter_ingestion_specs(target="bots", url_override=None)
    urls = {url for url, _ in specs}
    assert "https://the-tower-idle-tower-defense.fandom.com/wiki/Bot_Bot#Cost" in urls


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


def test_fetch_html_fandom_fallback_uses_parse_api(monkeypatch) -> None:
    """Fandom 403 responses should fall back to the MediaWiki parse API."""

    def fake_fetch_html(_url: str) -> str:
        raise urllib.error.HTTPError(
            "https://the-tower-idle-tower-defense.fandom.com/wiki/Guardian",
            403,
            "Forbidden",
            HTTPMessage(),
            None,
        )

    class FakeResponse:
        def __init__(self, payload: str) -> None:
            self._payload = payload
            self.headers = {"Content-Type": "application/json; charset=utf-8"}

        def read(self) -> bytes:
            return self._payload.encode("utf-8")

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

    def fake_urlopen(request, timeout=30):
        assert "api.php" in request.full_url
        return FakeResponse('{"parse": {"text": "<table></table>"}}')

    monkeypatch.setattr(fetch_wiki_data, "_fetch_html_via_request", fake_fetch_html)
    monkeypatch.setattr(fetch_wiki_data.urllib.request, "urlopen", fake_urlopen)

    html = fetch_wiki_data._fetch_html(
        "https://the-tower-idle-tower-defense.fandom.com/wiki/Guardian"
    )
    assert html == "<table></table>"


@pytest.mark.regression
def test_is_fandom_url_accepts_fandom_hosts() -> None:
    """Host validation accepts canonical Fandom domains only."""

    assert fetch_wiki_data._is_fandom_url("https://the-tower-idle-tower-defense.fandom.com/wiki/Guardian") is True
    assert fetch_wiki_data._is_fandom_url("https://fandom.com/wiki/Test") is True
    assert fetch_wiki_data._is_fandom_url("https://subdomain.FANDOM.com/wiki/Test") is True


@pytest.mark.regression
def test_is_fandom_url_rejects_suffix_and_userinfo_bypass_hosts() -> None:
    """Host validation rejects crafted domains that only contain fandom.com as a substring."""

    assert fetch_wiki_data._is_fandom_url("https://evilfandom.com/wiki/Test") is False
    assert fetch_wiki_data._is_fandom_url("https://fandom.com.evil.test/wiki/Test") is False
    assert fetch_wiki_data._is_fandom_url("https://fandom.com@evil.test/wiki/Test") is False
    assert fetch_wiki_data._is_fandom_url("https:///wiki/Test") is False

"""Tests for MkDocs reference navigation."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def test_mkdocs_reference_nav_includes_api_reference_pages() -> None:
    """Ensure Reference nav includes mkdocstrings-backed module pages."""

    repo_root = Path(__file__).resolve().parents[1]
    mkdocs_path = repo_root / "mkdocs.yml"
    config = yaml.safe_load(mkdocs_path.read_text(encoding="utf-8"))

    nav = config["nav"]
    reference_items = None
    for item in nav:
        if isinstance(item, dict) and "Reference" in item:
            reference_items = item["Reference"]
            break

    assert isinstance(reference_items, list)

    reference_map: dict[str, str] = {}
    for entry in reference_items:
        if isinstance(entry, dict):
            title, path = next(iter(entry.items()))
            if isinstance(path, str):
                reference_map[title] = path

    expected = {
        "Analytics": "reference/analytics.md",
        "Core Charting": "reference/core_charting.md",
        "Core Parsers": "reference/core_parsers.md",
    }
    for title, relpath in expected.items():
        assert reference_map.get(title) == relpath
        assert (repo_root / "docs" / relpath).exists()


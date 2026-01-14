"""Tests for MkDocs Reference navigation."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def test_mkdocs_reference_includes_explore_dsl() -> None:
    """Ensure Explore DSL page is listed under Reference."""

    repo_root = Path(__file__).resolve().parents[1]
    mkdocs_path = repo_root / "mkdocs.yml"
    config = yaml.safe_load(mkdocs_path.read_text(encoding="utf-8"))

    nav = config.get("nav", [])
    ref_section = next(
        (item for item in nav if isinstance(item, dict) and "Reference" in item),
        {},
    )
    ref_items = ref_section.get("Reference", []) if isinstance(ref_section, dict) else []
    explore_entry = next((item for item in ref_items if "Explore DSL" in item), None)
    assert explore_entry == {"Explore DSL": "explore_dsl.md"}
    assert (repo_root / "docs" / "explore_dsl.md").exists()

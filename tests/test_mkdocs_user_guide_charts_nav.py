"""Tests for MkDocs User Guide navigation."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def test_mkdocs_user_guide_charts_nav_includes_chart_builder_page() -> None:
    """Ensure Charts User Guide nests the Chart Builder page."""

    repo_root = Path(__file__).resolve().parents[1]
    mkdocs_path = repo_root / "mkdocs.yml"
    config = yaml.safe_load(mkdocs_path.read_text(encoding="utf-8"))

    nav = config["nav"]
    user_guide_items = None
    for item in nav:
        if isinstance(item, dict) and "User Guide" in item:
            user_guide_items = item["User Guide"]
            break

    assert isinstance(user_guide_items, list)

    charts_section = None
    for entry in user_guide_items:
        if isinstance(entry, dict) and "Charts" in entry:
            charts_section = entry["Charts"]
            break

    assert isinstance(charts_section, list)

    charts_map: dict[str, str] = {}
    for entry in charts_section:
        if isinstance(entry, dict):
            title, path = next(iter(entry.items()))
            if isinstance(path, str):
                charts_map[title] = path

    assert charts_map.get("Overview") == "charts.md"
    assert charts_map.get("Chart Builder") == "charts/chart_builder.md"
    assert (repo_root / "docs" / "charts" / "chart_builder.md").exists()


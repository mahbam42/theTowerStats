"""Tests for MkDocs Explore navigation."""

from __future__ import annotations

import pytest
import yaml
from pathlib import Path
from typing import Any

pytestmark = pytest.mark.unit


def test_mkdocs_user_guide_includes_explore_page() -> None:
    """Ensure Explore page is listed under User Guide."""

    repo_root = Path(__file__).resolve().parents[1]
    mkdocs_path = repo_root / "mkdocs.yml"
    config = yaml.safe_load(mkdocs_path.read_text(encoding="utf-8"))
    nav = config.get("nav", [])
    user_guide: dict[str, Any] = next(
        (item for item in nav if isinstance(item, dict) and "User Guide" in item),
        {},
    )
    user_guide_items = user_guide.get("User Guide", []) if isinstance(user_guide, dict) else []
    explore_entry = next((item for item in user_guide_items if "Explore" in item), None)
    assert explore_entry == {"Explore": "explore.md"}
    assert (repo_root / "docs" / "explore.md").exists()

"""Tests for MkDocs Project navigation."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

pytestmark = pytest.mark.unit


def test_mkdocs_project_nav_includes_repo_docs() -> None:
    """Ensure Project nav includes repo docs and App Philosophy."""
    repo_root = Path(__file__).resolve().parents[1]
    mkdocs_path = repo_root / "mkdocs.yml"
    config = yaml.safe_load(mkdocs_path.read_text(encoding="utf-8"))

    nav = config["nav"]
    project_section = None
    for item in nav:
        if isinstance(item, dict) and "Project" in item:
            project_section = item["Project"]
            break

    assert isinstance(project_section, list)

    project_map: dict[str, str] = {}
    for entry in project_section:
        if isinstance(entry, dict):
            title, path = next(iter(entry.items()))
            if isinstance(path, str):
                project_map[title] = path

    expected = {
        "Changelog": "repo/CHANGELOG.md",
        "Readme": "repo/readme.md",
        "Contributing": "repo/CONTRIBUTING.md",
        "Versioning": "repo/VERSIONING.md",
        "Security": "repo/SECURITY.md",
        "App Philosophy": "philosophy.md",
        "Design Philosophy": "design_philosophy.md",
        "Code of Conduct": "repo/CODE_OF_CONDUCT.md",
    }

    for title, path in expected.items():
        assert project_map.get(title) == path
        if path.startswith("repo/"):
            source_name = path.split("/", 1)[1]
            assert (repo_root / source_name).exists()
        else:
            assert (repo_root / "docs" / path).exists()

"""Unit tests for the staging DB refresh script."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from types import ModuleType

import pytest

pytestmark = pytest.mark.unit


def load_script_module() -> ModuleType:
    """Load the refresh script as a module for unit testing."""
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "refresh_staging_db.py"
    spec = importlib.util.spec_from_file_location("refresh_staging_db", script_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_load_env_file_sets_missing_vars_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ensure .env loading does not override existing environment variables."""
    module = load_script_module()
    env_file = tmp_path / "sample.env"
    env_file.write_text("FOO=bar\nBAZ=qux\n", encoding="utf-8")

    monkeypatch.setenv("FOO", "existing")
    monkeypatch.delenv("BAZ", raising=False)

    module.load_env_file(env_file)

    assert os.environ["FOO"] == "existing"
    assert os.environ["BAZ"] == "qux"


def test_sql_literal_escapes_quotes() -> None:
    """Ensure SQL string literals are escaped safely."""
    module = load_script_module()

    assert module.sql_literal("simple") == "'simple'"
    assert module.sql_literal("ma'hbam") == "'ma''hbam'"


def test_topo_sort_orders_children_before_parents() -> None:
    """Ensure dependency ordering places children before parents."""
    module = load_script_module()

    nodes = ["child", "parent", "leaf"]
    edges = [("child", "parent")]

    ordered = module.topo_sort(nodes, edges)

    assert ordered.index("child") < ordered.index("parent")
    assert set(ordered) == {"child", "parent", "leaf"}


def test_build_prune_sql_includes_player_deletes() -> None:
    """Ensure the prune SQL includes child tables and final player delete."""
    module = load_script_module()

    sql = module.build_prune_sql("public", ["table_a", "table_b"], 42)

    assert "DELETE FROM public.table_a WHERE player_id <> 42;" in sql
    assert "DELETE FROM public.table_b WHERE player_id <> 42;" in sql
    assert "DELETE FROM public.player_state_player WHERE id <> 42;" in sql

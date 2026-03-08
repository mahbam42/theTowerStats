"""Unit tests for the staging DB refresh script."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace
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


@pytest.mark.regression
def test_main_runs_local_migrations_after_restore(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """Ensure snapshot refresh reapplies local migrations before pruning.

    Args:
        monkeypatch: Pytest environment patch helper.
        tmp_path: Temporary directory fixture.

    Returns:
        None.
    """

    module = load_script_module()
    commands: list[tuple[list[str], str, dict[str, str] | None]] = []

    monkeypatch.setattr(
        module,
        "parse_args",
        lambda: SimpleNamespace(
            env_file=str(tmp_path / ".env"),
            prod_url_var="PROD_READONLY_DATABASE_URL",
            local_url_var="LOCAL_DATABASE_URL",
            dump_path=str(tmp_path / "snapshot.dump"),
            schema="public",
            player_display_name="mahbam42",
            player_id=42,
            skip_migrate=False,
        ),
    )
    monkeypatch.setattr(module, "load_env_file", lambda path: None)
    monkeypatch.setattr(module, "require_tool", lambda name: None)
    monkeypatch.setattr(
        module,
        "run_command",
        lambda args, *, label, env=None: commands.append((args, label, env)),
    )
    monkeypatch.setattr(module, "fetch_player_tables", lambda db_url, schema: ["battle"])
    monkeypatch.setattr(module, "fetch_fk_edges", lambda db_url, schema, tables: [])
    monkeypatch.setattr(module, "topo_sort", lambda nodes, edges: list(nodes))
    monkeypatch.setattr(module, "build_prune_sql", lambda schema, tables, player_id: "SELECT 1;")
    monkeypatch.setattr(module, "run_psql", lambda sql, db_url: "")
    monkeypatch.setenv("PROD_READONLY_DATABASE_URL", "postgresql://prod")
    monkeypatch.setenv("LOCAL_DATABASE_URL", "postgresql://local")

    module.main()

    assert [label for _, label, _ in commands] == [
        "pg_dump",
        "pg_restore",
        "manage.py migrate",
    ]
    assert commands[2][2] is not None
    assert commands[2][2]["DATABASE_URL"] == "postgresql://local"

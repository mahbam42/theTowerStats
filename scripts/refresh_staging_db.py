#!/usr/bin/env python3
"""Refresh a local snapshot of production data and prune it to one player."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable


def load_env_file(path: Path) -> None:
    """Load environment variables from a .env file if not already set."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        key, sep, value = line.partition("=")
        if not sep:
            continue
        key = key.strip()
        value = value.strip()
        if value and value[0] in {"\"", "'"} and value[-1] == value[0]:
            value = value[1:-1]
        os.environ.setdefault(key, value)


def require_tool(name: str) -> None:
    """Ensure a required command-line tool is available in PATH."""
    if shutil.which(name) is None:
        raise RuntimeError(f"Missing required tool: {name}")


def run_command(
    args: list[str], *, label: str, env: dict[str, str] | None = None
) -> None:
    """Run a subprocess command and raise a clear error on failure.

    Args:
        args: Command and arguments to execute.
        label: Human-readable operation label for error messages.
        env: Optional environment variable mapping for the subprocess.

    Returns:
        None.
    """

    try:
        subprocess.run(args, check=True, env=env)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"{label} failed with exit code {exc.returncode}.") from exc


def run_local_migrations(manage_py_path: Path, *, local_db_url: str) -> None:
    """Apply local Django migrations after restoring the production snapshot.

    Args:
        manage_py_path: Path to the repository's ``manage.py`` entry point.
        local_db_url: Database URL that was restored and should be migrated.

    Returns:
        None.
    """

    migrate_env = os.environ.copy()
    migrate_env["DATABASE_URL"] = local_db_url
    run_command(
        [sys.executable, str(manage_py_path), "migrate", "--noinput"],
        label="manage.py migrate",
        env=migrate_env,
    )


def run_psql(sql: str, db_url: str) -> str:
    """Run a SQL statement via psql and return stdout."""
    result = subprocess.run(
        [
            "psql",
            db_url,
            "-v",
            "ON_ERROR_STOP=1",
            "-At",
            "-F",
            "\t",
            "-c",
            sql,
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def sql_literal(value: str) -> str:
    """Return a SQL string literal with single quotes escaped."""
    return "'" + value.replace("'", "''") + "'"


def get_player_id(db_url: str, schema: str, display_name: str) -> int:
    """Resolve a player id from display_name, failing if not unique."""
    sql = (
        "SELECT id "
        f"FROM {schema}.player_state_player "
        f"WHERE display_name = {sql_literal(display_name)};"
    )
    output = run_psql(sql, db_url)
    rows = [line for line in output.splitlines() if line]
    if not rows:
        raise RuntimeError(
            f"No player found for display_name={display_name!r} in {schema}."
        )
    if len(rows) > 1:
        raise RuntimeError(
            f"Multiple players found for display_name={display_name!r}: {rows}"
        )
    return int(rows[0])


def fetch_player_tables(db_url: str, schema: str) -> list[str]:
    """Return tables in a schema that include a player_id column."""
    sql = (
        "SELECT table_name "
        "FROM information_schema.columns "
        f"WHERE table_schema = {sql_literal(schema)} "
        "  AND column_name = 'player_id' "
        "ORDER BY table_name;"
    )
    output = run_psql(sql, db_url)
    return [line for line in output.splitlines() if line]


def fetch_fk_edges(
    db_url: str, schema: str, tables: Iterable[str]
) -> list[tuple[str, str]]:
    """Return foreign key edges between player-scoped tables."""
    qualified = {f"{schema}.{table}" for table in tables}
    sql = (
        "SELECT conrelid::regclass::text AS child_table, "
        "       confrelid::regclass::text AS parent_table "
        "FROM pg_constraint "
        "WHERE contype = 'f' "
        "  AND conrelid::regclass::text LIKE "
        f"    {sql_literal(schema + '.%')} "
        "  AND confrelid::regclass::text LIKE "
        f"    {sql_literal(schema + '.%')};"
    )
    output = run_psql(sql, db_url)
    edges: list[tuple[str, str]] = []
    for line in output.splitlines():
        if not line:
            continue
        child_table, parent_table = line.split("\t", maxsplit=1)
        if child_table in qualified and parent_table in qualified:
            edges.append(
                (
                    child_table.removeprefix(f"{schema}."),
                    parent_table.removeprefix(f"{schema}."),
                )
            )
    return edges


def topo_sort(nodes: Iterable[str], edges: Iterable[tuple[str, str]]) -> list[str]:
    """Topologically sort nodes so children appear before parents."""
    node_list = sorted(set(nodes))
    indegree: dict[str, int] = {node: 0 for node in node_list}
    adjacency: dict[str, set[str]] = {node: set() for node in node_list}

    for child, parent in edges:
        if child not in indegree or parent not in indegree:
            continue
        if parent in adjacency[child]:
            continue
        adjacency[child].add(parent)
        indegree[parent] += 1

    ready = sorted(node for node, degree in indegree.items() if degree == 0)
    ordered: list[str] = []

    while ready:
        node = ready.pop(0)
        ordered.append(node)
        for parent in sorted(adjacency[node]):
            indegree[parent] -= 1
            if indegree[parent] == 0:
                ready.append(parent)
                ready.sort()

    if len(ordered) != len(node_list):
        raise RuntimeError("Cycle detected in table dependencies; aborting prune.")

    return ordered


def build_prune_sql(schema: str, tables: Iterable[str], player_id: int) -> str:
    """Build transactional SQL to delete non-target player rows."""
    lines = ["BEGIN;"]
    for table in tables:
        lines.append(
            f"DELETE FROM {schema}.{table} WHERE player_id <> {player_id};"
        )
    lines.append(
        f"DELETE FROM {schema}.player_state_player WHERE id <> {player_id};"
    )
    lines.append("COMMIT;")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments for the refresh script."""
    parser = argparse.ArgumentParser(
        description=(
            "Dump production data, restore into local Postgres, and prune to one player."
        )
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to a .env file containing database URLs.",
    )
    parser.add_argument(
        "--prod-url-var",
        default="PROD_READONLY_DATABASE_URL",
        help="Environment variable name for the production read-only URL.",
    )
    parser.add_argument(
        "--local-url-var",
        default="LOCAL_DATABASE_URL",
        help="Environment variable name for the local database URL.",
    )
    parser.add_argument(
        "--dump-path",
        default="/tmp/thetowerstats.dump",
        help="Path to write the pg_dump custom-format file.",
    )
    parser.add_argument(
        "--schema",
        default="public",
        help="Schema containing player data.",
    )
    parser.add_argument(
        "--player-display-name",
        default="mahbam42",
        help="Player display name to keep in the local snapshot.",
    )
    parser.add_argument(
        "--player-id",
        type=int,
        default=None,
        help="Player id to keep (overrides display-name lookup).",
    )
    parser.add_argument(
        "--skip-migrate",
        action="store_true",
        help="Skip applying local Django migrations after restoring the snapshot.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the full refresh flow from prod dump through local prune."""
    args = parse_args()

    load_env_file(Path(args.env_file))

    prod_url = os.getenv(args.prod_url_var)
    local_url = os.getenv(args.local_url_var)

    if not prod_url:
        raise RuntimeError(f"Missing environment variable: {args.prod_url_var}")
    if not local_url:
        raise RuntimeError(f"Missing environment variable: {args.local_url_var}")

    require_tool("pg_dump")
    require_tool("pg_restore")
    require_tool("psql")

    dump_path = Path(args.dump_path)
    repo_root = Path(__file__).resolve().parents[1]
    manage_py_path = repo_root / "manage.py"

    print("Dumping production database...")
    run_command(
        [
            "pg_dump",
            "-Fc",
            "--no-owner",
            "--no-acl",
            "-f",
            str(dump_path),
            prod_url,
        ],
        label="pg_dump",
    )

    print("Restoring into local database...")
    run_command(
        [
            "pg_restore",
            "--clean",
            "--if-exists",
            "--no-owner",
            "--no-acl",
            "-d",
            local_url,
            str(dump_path),
        ],
        label="pg_restore",
    )

    if not args.skip_migrate:
        print("Applying local Django migrations...")
        run_local_migrations(manage_py_path, local_db_url=local_url)

    if args.player_id is None:
        player_id = get_player_id(local_url, args.schema, args.player_display_name)
    else:
        player_id = args.player_id

    print(f"Pruning local data to player id {player_id}...")
    tables = fetch_player_tables(local_url, args.schema)
    if not tables:
        raise RuntimeError("No tables with player_id found; aborting prune.")

    edges = fetch_fk_edges(local_url, args.schema, tables)
    delete_order = topo_sort(tables, edges)
    prune_sql = build_prune_sql(args.schema, delete_order, player_id)

    run_psql(prune_sql, local_url)

    print("Refresh complete.")


if __name__ == "__main__":
    main()

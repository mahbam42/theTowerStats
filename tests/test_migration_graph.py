"""Regression tests for Django migration graph integrity."""

from __future__ import annotations

import pytest
from django.db import connections
from django.db.migrations.loader import MigrationLoader

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_player_state_migrations_have_single_leaf() -> None:
    """Assert `player_state` has a single leaf migration.

    This prevents accidental divergent migration branches that require a merge.
    """

    loader = MigrationLoader(connections["default"])
    leaves = [node for node in loader.graph.leaf_nodes() if node[0] == "player_state"]

    assert len(leaves) == 1, f"Unexpected leaf nodes: {leaves}"

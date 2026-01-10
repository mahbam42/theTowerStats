"""Unit tests for the deploy_railway management command."""

from __future__ import annotations

from unittest.mock import ANY, call, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError


@pytest.mark.unit
def test_deploy_railway_runs_steps_in_order() -> None:
    """Ensure deploy_railway runs migration, wiki rebuild, and reparse in order."""

    with patch("core.management.commands.deploy_railway.call_command") as mocked:
        call_command("deploy_railway", write=True)
        assert mocked.call_args_list == [
            call("migrate", interactive=False, verbosity=ANY),
            call("rebuild_wiki_definitions", target="all", write=True, verbosity=ANY),
            call("reparse_battle_reports", write=True, verbosity=ANY),
        ]


@pytest.mark.unit
def test_deploy_railway_skip_flags() -> None:
    """Allow skipping deploy_railway steps via flags."""

    with patch("core.management.commands.deploy_railway.call_command") as mocked:
        call_command("deploy_railway", write=True, skip_wiki=True, skip_reparse=True)
        assert mocked.call_args_list == [call("migrate", interactive=False, verbosity=ANY)]


@pytest.mark.unit
def test_deploy_railway_requires_write_flag() -> None:
    """Require explicit intent before running deploy steps."""

    with pytest.raises(CommandError, match="--write"):
        call_command("deploy_railway")

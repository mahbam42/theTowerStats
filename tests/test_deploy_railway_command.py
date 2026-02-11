"""Unit tests for the deploy_railway management command."""

from __future__ import annotations

import os
from unittest.mock import ANY, call, patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from core.management.commands import deploy_railway


@pytest.mark.unit
def test_deploy_railway_runs_steps_in_order() -> None:
    """Ensure deploy_railway runs migration, wiki rebuild, and reparse in order."""

    steps: list[tuple[str, tuple, dict]] = []

    def record_call_command(*args, **kwargs) -> None:
        steps.append(("call_command", args, kwargs))

    def record_rebuild(*args, **kwargs) -> deploy_railway.WikiRebuildResult:
        steps.append(("rebuild_wiki", args, kwargs))
        return deploy_railway.WikiRebuildResult(completed=True, reason=None)

    with patch(
        "core.management.commands.deploy_railway.call_command", side_effect=record_call_command
    ), patch("core.management.commands.deploy_railway._run_wiki_rebuild", side_effect=record_rebuild):
        call_command("deploy_railway", write=True)

    assert len(steps) == 3
    assert steps[0][0] == "call_command"
    assert steps[0][1] == ("migrate",)
    assert steps[0][2]["interactive"] is False
    assert "verbosity" in steps[0][2]

    assert steps[1][0] == "rebuild_wiki"
    assert steps[1][2]["offline_wiki"] is False
    assert steps[1][2]["timeout_seconds"] == deploy_railway.DEFAULT_WIKI_REBUILD_TIMEOUT_SECONDS

    assert steps[2][0] == "call_command"
    assert steps[2][1] == ("reparse_battle_reports",)
    assert steps[2][2]["write"] is True


@pytest.mark.unit
def test_deploy_railway_skip_flags() -> None:
    """Allow skipping deploy_railway steps via flags."""

    with patch("core.management.commands.deploy_railway.call_command") as mocked, patch(
        "core.management.commands.deploy_railway._run_wiki_rebuild"
    ) as mocked_rebuild:
        call_command("deploy_railway", write=True, skip_wiki=True, skip_reparse=True)
        assert mocked.call_args_list == [call("migrate", interactive=False, verbosity=ANY)]
        mocked_rebuild.assert_not_called()


@pytest.mark.unit
def test_deploy_railway_requires_write_flag() -> None:
    """Require explicit intent before running deploy steps."""

    with pytest.raises(CommandError, match="--write"):
        call_command("deploy_railway")


@pytest.mark.unit
def test_deploy_railway_offline_wiki_env_skips_fetch() -> None:
    """Allow offline wiki rebuilds via environment toggle."""

    with patch.dict(os.environ, {"TOWERSTATS_WIKI_OFFLINE": "1"}), patch(
        "core.management.commands.deploy_railway.call_command"
    ) as mocked, patch("core.management.commands.deploy_railway._run_wiki_rebuild") as mocked_rebuild:
        call_command("deploy_railway", write=True)
        assert mocked.call_args_list == [
            call("migrate", interactive=False, verbosity=ANY),
            call("reparse_battle_reports", write=True, verbosity=ANY),
        ]
        assert mocked_rebuild.call_args.kwargs["offline_wiki"] is True


@pytest.mark.unit
def test_deploy_railway_continues_after_timeout() -> None:
    """Continue the deploy pipeline when the wiki rebuild times out."""

    with patch("core.management.commands.deploy_railway.call_command") as mocked, patch(
        "core.management.commands.deploy_railway._run_wiki_rebuild",
        return_value=deploy_railway.WikiRebuildResult(completed=False, reason="timeout"),
    ):
        call_command("deploy_railway", write=True)
        assert mocked.call_args_list == [
            call("migrate", interactive=False, verbosity=ANY),
            call("reparse_battle_reports", write=True, verbosity=ANY),
        ]


@pytest.mark.unit
def test_run_wiki_rebuild_times_out() -> None:
    """Return False when the wiki rebuild exceeds the timeout."""

    with patch(
        "core.management.commands.deploy_railway.subprocess.run",
        side_effect=deploy_railway.subprocess.TimeoutExpired(cmd="rebuild", timeout=1),
    ):
        result = deploy_railway._run_wiki_rebuild(
            offline_wiki=False,
            verbosity=1,
            timeout_seconds=1,
        )
    assert result.completed is False
    assert result.reason == "timed out after 1s"


@pytest.mark.unit
def test_run_wiki_rebuild_handles_exit_code_failure() -> None:
    """Return False when the wiki rebuild exits non-zero."""

    with patch(
        "core.management.commands.deploy_railway.subprocess.run",
        side_effect=deploy_railway.subprocess.CalledProcessError(returncode=2, cmd=["rebuild"]),
    ):
        result = deploy_railway._run_wiki_rebuild(
            offline_wiki=False,
            verbosity=1,
            timeout_seconds=1,
        )
    assert result.completed is False
    assert result.reason == "exit code 2"

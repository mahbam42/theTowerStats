"""Integration tests for Battle History preset tagging and snapshots."""

from __future__ import annotations

import pytest
from django.urls import reverse

from core.services import ingest_battle_report
from gamedata.models import BattleReportProgress
from player_state.models import Preset


def _battle_report_text(*, wave: int) -> str:
    """Return a minimal Battle Report payload string for ingestion tests."""

    return "\n".join(
        [
            "Battle Report",
            "Battle Date: 2025-12-01 13:45:00",
            "Tier: 6",
            f"Wave: {wave}",
            "Real Time: 1h 2m 3s",
            "Killed By: Boss",
            "Coins Earned: 1.00M",
        ]
    )


@pytest.mark.django_db
def test_ingest_sets_preset_snapshots_and_survives_preset_delete(player) -> None:
    """Preset snapshot fields remain readable after the preset row is deleted."""

    report, _ = ingest_battle_report(_battle_report_text(wave=101), player=player, preset_name="Farming")
    progress = report.run_progress
    assert progress.preset is not None
    assert progress.preset_name_snapshot == "Farming"
    assert progress.preset_color_snapshot

    preset_id = progress.preset_id
    preset_color = progress.preset_color_snapshot
    Preset.objects.filter(id=preset_id).delete()

    progress.refresh_from_db()
    assert progress.preset is None
    assert progress.preset_name_snapshot == "Farming"
    assert progress.preset_color_snapshot == preset_color


@pytest.mark.django_db
def test_battle_history_filters_by_preset(auth_client, player) -> None:
    """Preset filter limits the visible run rows."""

    ingest_battle_report(_battle_report_text(wave=111), player=player, preset_name="Farm")
    ingest_battle_report(_battle_report_text(wave=222), player=player, preset_name="Push")

    farm = Preset.objects.get(player=player, name="Farm")

    response = auth_client.get(reverse("core:battle_history"), data={"preset": farm.id})
    assert response.status_code == 200

    content = response.content.decode("utf-8")
    assert "111" in content
    assert "222" not in content


@pytest.mark.django_db
def test_battle_history_allows_manual_preset_update(auth_client, player) -> None:
    """Manual preset assignment updates the FK and snapshot fields."""

    report, _ = ingest_battle_report(_battle_report_text(wave=333), player=player, preset_name=None)
    progress = report.run_progress
    assert progress.preset is None
    assert progress.preset_name_snapshot == ""

    preset = Preset.objects.create(player=player, name="Late Tag")

    url = reverse("core:battle_history")
    response = auth_client.post(
        url,
        data={
            "action": "update_run_preset",
            "progress_id": progress.id,
            "preset": preset.id,
            "next": url,
        },
    )
    assert response.status_code == 302

    progress.refresh_from_db()
    assert progress.preset_id == preset.id
    assert progress.preset_name_snapshot == "Late Tag"
    assert progress.preset_color_snapshot

    response = auth_client.post(
        url,
        data={
            "action": "update_run_preset",
            "progress_id": progress.id,
            "preset": "",
            "next": url,
        },
    )
    assert response.status_code == 302

    progress.refresh_from_db()
    assert progress.preset is None
    assert progress.preset_name_snapshot == ""
    assert progress.preset_color_snapshot == ""


@pytest.mark.django_db
def test_battle_history_rejects_unknown_progress_id(auth_client, player) -> None:
    """Unknown progress ids do not crash the update endpoint."""

    preset = Preset.objects.create(player=player, name="Tag")

    response = auth_client.post(
        reverse("core:battle_history"),
        data={
            "action": "update_run_preset",
            "progress_id": 999_999,
            "preset": preset.id,
        },
    )
    assert response.status_code == 302
    assert BattleReportProgress.objects.count() == 0

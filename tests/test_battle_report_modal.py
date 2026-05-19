"""Integration tests for the Battle Report modal payload."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from gamedata.models import BattleReport, BattleReportProgress

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_battle_report_modal_payload_includes_metrics_and_raw_text(auth_client, player) -> None:
    """Modal payload returns raw text and metric link metadata."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="z" * 64,
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        tier=2,
        wave=100,
        real_time_seconds=600,
        coins_earned=1200,
        coins_earned_raw="1,200",
        gem_blocks_tapped=3,
    )

    response = auth_client.get(reverse("core:battle_report_modal", args=[report.id]))
    assert response.status_code == 200

    payload = response.json()
    assert payload["ok"] is True
    assert payload["report"]["raw_text"].startswith("Battle Report")
    assert payload["report"]["run_number"] == 1

    metrics = {metric["key"]: metric for metric in payload["report"]["metrics"]}
    assert metrics["coins_earned"]["chart_id"] == "coins_earned"
    assert metrics["coins_per_hour"]["value"] == "7,200.00"
    assert metrics["coins_earned"]["numeric_value"] == 1200
    assert metrics["coins_earned"]["unit"] == "coins"
    assert metrics["gem_blocks_tapped"]["chart_id"] is None
    assert metrics["interest_earned"]["value"] == "—"


@pytest.mark.django_db
def test_battle_report_modal_run_number_is_player_scoped(auth_client, player) -> None:
    """Modal run numbers use player-scoped ordering."""

    user_model = get_user_model()
    other_user = user_model.objects.create_user(username="bob", password="password")
    other_player = other_user.player

    for idx in range(2):
        report = BattleReport.objects.create(
            player=other_player,
            raw_text="Battle Report\nCoins earned    1,200\n",
            checksum=(f"other-{idx}".ljust(64, "x")),
        )
        BattleReportProgress.objects.create(
            battle_report=report,
            player=other_player,
            battle_date=datetime(2025, 12, idx + 1, tzinfo=timezone.utc),
            tier=1,
            wave=100,
            real_time_seconds=600,
            coins_earned=1200,
        )

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    2,400\n",
        checksum="player-report".ljust(64, "y"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 3, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
        coins_earned=2400,
    )

    response = auth_client.get(reverse("core:battle_report_modal", args=[report.id]))
    assert response.status_code == 200

    payload = response.json()
    assert payload["report"]["run_number"] == 1


@pytest.mark.django_db
def test_battle_report_modal_marks_fallback_battle_date(auth_client, player) -> None:
    """Modal payload marks fallback battle dates."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="fallback-date".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=report.parsed_at,
        tier=2,
        wave=100,
        real_time_seconds=600,
    )

    response = auth_client.get(reverse("core:battle_report_modal", args=[report.id]))
    assert response.status_code == 200

    payload = response.json()
    assert payload["report"]["battle_date_fallback"] is True


@pytest.mark.django_db
@pytest.mark.regression
def test_battle_report_modal_formats_dissonance_metrics_to_three_decimals(auth_client, player) -> None:
    """Dissonance metric rows in the modal should display exactly three decimals."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="dissonance-rounding".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        tier=8,
        wave=1678,
        real_time_seconds=600,
        dissonance_levels_snapshot={"attack": 1, "defense": 1, "utility": 3, "ultimate_weapon": 1},
    )

    response = auth_client.get(reverse("core:battle_report_modal", args=[report.id]))
    assert response.status_code == 200

    payload = response.json()
    metrics = {metric["key"]: metric for metric in payload["report"]["metrics"]}
    assert metrics["dissonance_utility"]["value"] == "x1.296"


@pytest.mark.django_db
@pytest.mark.regression
def test_battle_report_modal_clamps_utility_dissonance_snapshot_to_three_x(auth_client, player) -> None:
    """Utility Dissonance display should stay at the 3x cap for higher stored snapshot levels."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="dissonance-utility-cap".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2026, 1, 2, 12, 0, tzinfo=timezone.utc),
        tier=8,
        wave=1959,
        real_time_seconds=600,
        dissonance_levels_snapshot={"attack": 1, "defense": 1, "utility": 9, "ultimate_weapon": 1},
    )

    response = auth_client.get(reverse("core:battle_report_modal", args=[report.id]))
    assert response.status_code == 200

    payload = response.json()
    metrics = {metric["key"]: metric for metric in payload["report"]["metrics"]}
    assert metrics["dissonance_utility"]["value"] == "x1.388"

@pytest.mark.django_db
@pytest.mark.regression
def test_battle_report_modal_post_updates_special_run(auth_client, player) -> None:
    """Modal POST updates special-run fields and returns refreshed payload."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="modal-update".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        tier=8,
        wave=2500,
        real_time_seconds=600,
    )

    response = auth_client.post(
        reverse("core:battle_report_modal", args=[report.id]),
        data={"special_run": "dissonance", "special_run_detail": "utility"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 200

    report.refresh_from_db()
    progress = report.run_progress
    assert progress.is_dissonance is True
    assert progress.dissonance_type == "utility"
    assert progress.is_tournament is False
    assert progress.tournament_rank is None

    payload = response.json()
    assert payload["report"]["special_run"] == "dissonance"
    assert payload["report"]["special_run_detail"] == "utility"
    assert payload["report"]["dissonance_type_label"] == "Utility"


@pytest.mark.django_db
@pytest.mark.regression
def test_battle_report_modal_post_clears_previous_dissonance_when_switching_to_tournament(
    auth_client, player
) -> None:
    """Modal POST keeps Tournament and Dissonance mutually exclusive."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="modal-switch".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        tier=8,
        wave=2500,
        real_time_seconds=600,
        is_dissonance=True,
        dissonance_type="attack",
    )

    response = auth_client.post(
        reverse("core:battle_report_modal", args=[report.id]),
        data={"special_run": "tournament", "special_run_detail": "gold"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 200

    report.refresh_from_db()
    progress = report.run_progress
    assert progress.is_tournament is True
    assert progress.tournament_rank == "gold"
    assert progress.is_dissonance is False
    assert progress.dissonance_type is None


@pytest.mark.django_db
def test_battle_report_modal_post_rejects_invalid_special_run_detail(auth_client, player) -> None:
    """Modal POST validates dependent special-run detail values."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum="modal-invalid".ljust(64, "x"),
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        tier=8,
        wave=2500,
        real_time_seconds=600,
    )

    response = auth_client.post(
        reverse("core:battle_report_modal", args=[report.id]),
        data={"special_run": "dissonance", "special_run_detail": ""},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 400
    assert "special_run_detail" in response.json()["errors"]

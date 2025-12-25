"""Phase 8 Pillar 3 integration tests (demo mode + lightweight exports)."""

from __future__ import annotations

import csv
import io

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.demo import DEMO_SESSION_KEY
from core.services import ingest_battle_report
from gamedata.models import BattleReport
from player_state.models import Player

pytestmark = pytest.mark.integration


def _battle_report_text(*, battle_date: str, wave: int, coins: str) -> str:
    """Return a minimal Battle Report payload string for ingestion tests."""

    return "\n".join(
        [
            "Battle Report",
            f"Battle Date: {battle_date}",
            "Tier: 6",
            f"Wave: {wave}",
            "Real Time: 1h 0m 0s",
            "Killed By: Boss",
            f"Coins Earned: {coins}",
        ]
    )


@pytest.mark.django_db
def test_demo_mode_scopes_views_to_demo_player(auth_client, player) -> None:
    """Demo mode renders the shared demo dataset instead of the user's data."""

    user_report, _ = ingest_battle_report(
        _battle_report_text(battle_date="2025-12-01 13:45:00", wave=222, coins="1.00M"),
        player=player,
        preset_name=None,
    )

    user_model = get_user_model()
    demo_user = user_model.objects.create(username="__demo__")
    demo_user.set_unusable_password()
    demo_user.save(update_fields=["password"])
    demo_player, _ = Player.objects.get_or_create(user=demo_user, defaults={"display_name": "Demo Player"})

    demo_report, _ = ingest_battle_report(
        _battle_report_text(battle_date="2025-12-02 13:45:00", wave=111, coins="2.00M"),
        player=demo_player,
        preset_name="Demo",
    )

    assert user_report.player_id == player.id
    assert demo_report.player_id == demo_player.id

    response = auth_client.post(reverse("core:enable_demo_mode"), data={"next": reverse("core:battle_history")})
    assert response.status_code == 302

    response = auth_client.get(reverse("core:battle_history"))
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "Demo mode" in content
    assert "111" in content
    assert "222" not in content


@pytest.mark.django_db
def test_demo_mode_rejects_writes(auth_client, player) -> None:
    """Demo mode blocks imports and other write actions."""

    user_model = get_user_model()
    demo_user = user_model.objects.create(username="__demo__")
    demo_user.set_unusable_password()
    demo_user.save(update_fields=["password"])
    demo_player, _ = Player.objects.get_or_create(user=demo_user, defaults={"display_name": "Demo Player"})
    ingest_battle_report(
        _battle_report_text(battle_date="2025-12-02 13:45:00", wave=111, coins="2.00M"),
        player=demo_player,
        preset_name="Demo",
    )

    session = auth_client.session
    session[DEMO_SESSION_KEY] = True
    session.save()

    before = BattleReport.objects.count()
    response = auth_client.post(
        reverse("core:dashboard"),
        data={
            "raw_text": _battle_report_text(battle_date="2025-12-03 13:45:00", wave=333, coins="3.00M"),
            "preset_name": "",
        },
    )
    assert response.status_code == 302
    assert BattleReport.objects.count() == before


@pytest.mark.django_db
def test_export_derived_metrics_csv_returns_csv_snapshot(auth_client, player) -> None:
    """CSV export returns derived datasets only for the active player's filters."""

    ingest_battle_report(
        _battle_report_text(battle_date="2025-12-10 13:45:00", wave=100, coins="1.00M"),
        player=player,
        preset_name=None,
    )
    ingest_battle_report(
        _battle_report_text(battle_date="2025-12-11 13:45:00", wave=200, coins="2.00M"),
        player=player,
        preset_name=None,
    )

    response = auth_client.get(
        reverse("core:export_derived_metrics_csv"),
        data={"charts": ["coins_per_wave"], "start_date": "2025-12-09", "end_date": "2025-12-22"},
    )
    assert response.status_code == 200
    assert response["Content-Type"].startswith("text/csv")

    reader = csv.reader(io.StringIO(response.content.decode("utf-8")))
    header = next(reader)
    assert header[0] == "date"
    assert "coins_per_wave:Coins per Wave" in header

    rows = list(reader)
    assert {row[0] for row in rows} == {"2025-12-10", "2025-12-11"}
    idx = header.index("coins_per_wave:Coins per Wave")
    exported = {row[0]: row[idx] for row in rows}
    assert exported["2025-12-10"] not in ("", None)
    assert exported["2025-12-11"] not in ("", None)


@pytest.mark.django_db
def test_signup_rejects_reserved_demo_username(client) -> None:
    """Signup rejects the reserved demo username to avoid collisions."""

    response = client.post(
        reverse("login"),
        data={
            "signup_submit": "1",
            "username": "__demo__",
            "password1": "a-strong-password-123",
            "password2": "a-strong-password-123",
        },
    )
    assert response.status_code == 200
    assert "reserved" in response.content.decode("utf-8").lower()

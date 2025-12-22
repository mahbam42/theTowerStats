"""Django integration tests for Battle History table rendering."""

from __future__ import annotations

import pytest
from django.urls import reverse

from core.services import ingest_battle_report
from gamedata.models import BattleReport

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_battle_history_renders_import_widget_and_sort_links(auth_client, player) -> None:
    """Battle History includes quick import and clickable sort headers."""

    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-01 13:45:00",
                "Tier: 6",
                "Wave: 1234",
                "Real Time: 1h 2m 3s",
                "Killed By: Boss",
                "Coins Earned: 1.00M",
            ]
        ),
        player=player,
    )

    response = auth_client.get(reverse("core:battle_history"))
    assert response.status_code == 200

    content = response.content.decode("utf-8")
    assert "Add Battle Report" in content
    assert "Import Battle Report" in content
    assert "<details" in content
    assert "sort=run_progress__battle_date" in content
    assert "sort=-run_progress__wave" in content
    assert "sort=-run_progress__coins_earned" in content
    assert "Highest wave" in content
    assert "1234" in content
    assert "Gem blocks" in content


@pytest.mark.django_db
def test_battle_history_import_panel_opens_on_form_errors(auth_client) -> None:
    """Import panel expands when the import form is invalid."""

    response = auth_client.post(reverse("core:battle_history"), data={})
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "<details open" in content
    assert "This field is required." in content


@pytest.mark.django_db
def test_battle_history_import_accepts_space_separated_headers(auth_client, player) -> None:
    """Import accepts reports where headers are separated by multiple spaces."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date  Dec 21, 2025 13:18",
            "Tier  8",
            "Wave  1141",
            "Real Time  2h 46m 15s",
            "Coins earned  16.89M",
        ]
    )
    response = auth_client.post(reverse("core:battle_history"), data={"raw_text": raw_text}, follow=True)
    assert response.status_code == 200

    assert BattleReport.objects.filter(player=player).count() == 1
    assert "1141" in response.content.decode("utf-8")


@pytest.mark.django_db
def test_battle_history_import_allows_missing_battle_date(auth_client, player) -> None:
    """Import allows reports missing Battle Date and stores a null battle date."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Game Time\t1d 9h 39m 5s",
            "Real Time\t9h 3m 18s",
            "Tier\t1",
            "Wave\t3656",
            "Killed By\tFast",
            "Coins earned\t17.29M",
        ]
    )
    response = auth_client.post(reverse("core:battle_history"), data={"raw_text": raw_text}, follow=True)
    assert response.status_code == 200

    report = BattleReport.objects.get(player=player)
    assert report.run_progress.battle_date is None


@pytest.mark.django_db
def test_battle_history_import_accepts_single_space_separators(auth_client, player) -> None:
    """Import accepts reports when the clipboard collapses tabs into single spaces."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date Dec 22, 2025 14:56",
            "Game Time 1d 9h 39m 5s",
            "Real Time 9h 3m 18s",
            "Tier 1",
            "Wave 3656",
            "Killed By Fast",
            "Coins earned 17.29M",
        ]
    )
    response = auth_client.post(reverse("core:battle_history"), data={"raw_text": raw_text}, follow=True)
    assert response.status_code == 200

    report = BattleReport.objects.get(player=player)
    assert report.run_progress.tier == 1
    assert report.run_progress.wave == 3656


@pytest.mark.django_db
def test_battle_history_import_accepts_crlf_newlines(auth_client, player) -> None:
    """Import accepts reports pasted via textarea submissions using CRLF newlines."""

    raw_text = "\r\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 22, 2025 14:56",
            "Real Time\t9h 3m 18s",
            "Tier\t1",
            "Wave\t3656",
        ]
    )
    response = auth_client.post(reverse("core:battle_history"), data={"raw_text": raw_text}, follow=True)
    assert response.status_code == 200

    report = BattleReport.objects.get(player=player)
    assert report.run_progress.tier == 1


@pytest.mark.django_db
def test_battle_history_includes_killed_by_donut_chart(auth_client, player) -> None:
    """Battle History includes a diagnostic Killed By donut chart."""

    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-01 13:45:00",
                "Tier: 6",
                "Wave: 1234",
                "Real Time: 1h 2m 3s",
                "Killed By: Boss",
                "Coins Earned: 1.00M",
            ]
        ),
        player=player,
    )

    response = auth_client.get(reverse("core:battle_history"))
    assert response.status_code == 200
    assert response.context["killed_by_donut_json"] is not None
    assert "Boss" in response.context["killed_by_donut_json"]
    assert "Killed By (diagnostic)" in response.content.decode("utf-8")


@pytest.mark.django_db
def test_battle_history_excludes_tournaments_by_default_and_can_opt_in(auth_client, player) -> None:
    """Tournament runs are excluded by default and can be explicitly included."""

    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-01 13:45:00",
                "Tier: 6",
                "Wave: 111",
                "Real Time: 1h 0m 0s",
                "Killed By: Boss",
                "Coins Earned: 1.00M",
            ]
        ),
        player=player,
    )
    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-02 13:45:00",
                "Tier: 3+",
                "Wave: 222",
                "Real Time: 1h 0m 0s",
                "Killed By: Boss",
                "Coins Earned: 1.00M",
            ]
        ),
        player=player,
    )

    response = auth_client.get(reverse("core:battle_history"))
    assert response.status_code == 200
    content = response.content.decode("utf-8")
    assert "111" in content
    assert "222" not in content


@pytest.mark.django_db
def test_battle_history_excludes_manual_tournaments_by_default(auth_client, player) -> None:
    """Runs tagged as tournament are excluded by default and can be included."""

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 22, 2025 14:56",
            "Real Time\t9h 3m 18s",
            "Tier\t1",
            "Wave\t3656",
        ]
    )
    response = auth_client.post(
        reverse("core:battle_history"),
        data={"raw_text": raw_text, "is_tournament": "on"},
        follow=True,
    )
    assert response.status_code == 200

    content = response.content.decode("utf-8")
    assert "3656" not in content

    response = auth_client.get(reverse("core:battle_history"), {"include_tournaments": "on"})
    assert response.status_code == 200
    assert "3656" in response.content.decode("utf-8")

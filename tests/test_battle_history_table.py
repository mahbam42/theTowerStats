"""Django integration tests for Battle History table rendering."""

from __future__ import annotations

import re

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
    sort_querystrings = response.context["sort_querystrings"]
    assert "sort=-run_progress__is_tournament" in sort_querystrings["tournament"]
    assert "sort=-derived_metrics__values__recovery_packages" in sort_querystrings["recovery_packages"]
    assert "Run #" in content
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
    """Import allows reports missing Battle Date and stores a fallback battle date."""

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
    assert report.run_progress.battle_date == report.parsed_at


@pytest.mark.django_db
def test_battle_history_marks_fallback_battle_date(auth_client, player) -> None:
    """Battle History marks imported timestamps when Battle Date is missing."""

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
    auth_client.post(reverse("core:battle_history"), data={"raw_text": raw_text}, follow=True)

    response = auth_client.get(reverse("core:battle_history"))
    assert response.status_code == 200
    assert "Imported" in response.content.decode("utf-8")


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
def test_battle_history_displays_coins_per_real_hour(auth_client, player) -> None:
    """Coins per real hour renders when coins and real time are available."""

    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-01 13:45:00",
                "Tier: 6",
                "Wave: 1234",
                "Real Time: 1h 0m 0s",
                "Coins Earned: 1.00M",
            ]
        ),
        player=player,
    )

    response = auth_client.get(reverse("core:battle_history"))
    assert response.status_code == 200

    content = response.content.decode("utf-8")
    assert 'data-format="unit-value"' in content
    assert 'data-unit="coins/hour"' in content
    assert 'data-value="1000000' in content


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
def test_battle_history_run_number_is_chronological(auth_client, player) -> None:
    """Run numbers reflect chronological order per player."""

    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-01 10:00:00",
                "Tier: 6",
                "Wave: 123",
                "Coins Earned: 1.00M",
            ]
        ),
        player=player,
    )
    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-03 10:00:00",
                "Tier: 7",
                "Wave: 456",
                "Coins Earned: 2.00M",
            ]
        ),
        player=player,
    )

    response = auth_client.get(reverse("core:battle_history"))
    assert response.status_code == 200

    ordered_ids = list(
        BattleReport.objects.filter(player=player)
        .select_related("run_progress")
        .order_by("run_progress__battle_date")
        .values_list("id", flat=True)
    )
    row_numbers = {row["run"].id: row["run_number"] for row in response.context["page_rows"]}
    assert row_numbers[ordered_ids[0]] == 1
    assert row_numbers[ordered_ids[1]] == 2


@pytest.mark.django_db
def test_battle_history_column_preferences_limit_columns(auth_client, player) -> None:
    """Column preferences restrict the table headers to selected columns."""

    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-01 10:00:00",
                "Tier: 6",
                "Wave: 123",
                "Coins Earned: 1.00M",
            ]
        ),
        player=player,
    )

    response = auth_client.post(
        reverse("core:battle_history"),
        data={
            "action": "update_column_preferences",
            "columns": ["run_number", "battle_date"],
            "next": reverse("core:battle_history"),
        },
        follow=True,
    )
    assert response.status_code == 200
    visible_keys = [column["key"] for column in response.context["visible_column_views"]]
    assert visible_keys == ["run_number", "battle_date"]


@pytest.mark.django_db
def test_battle_history_recovery_packages_column_is_hidden_by_default(auth_client, player) -> None:
    """Recovery packages stays hidden until selected in column preferences."""

    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-01 10:00:00",
                "Tier: 6",
                "Wave: 123",
                "Real Time: 1h 0m 0s",
                "Coins Earned: 1.00M",
                "Recovery Packages\t68",
            ]
        ),
        player=player,
    )

    response = auth_client.get(reverse("core:battle_history"))
    assert response.status_code == 200
    visible_keys = [column["key"] for column in response.context["visible_column_views"]]
    assert "recovery_packages" not in visible_keys

    response = auth_client.post(
        reverse("core:battle_history"),
        data={
            "action": "update_column_preferences",
            "columns": ["run_number", "recovery_packages"],
            "next": reverse("core:battle_history"),
        },
        follow=True,
    )
    assert response.status_code == 200
    visible_keys = [column["key"] for column in response.context["visible_column_views"]]
    assert visible_keys == ["run_number", "recovery_packages"]
    content = response.content.decode("utf-8")
    assert "Recovery packages" in content
    assert "68" in content


@pytest.mark.django_db
@pytest.mark.regression
def test_battle_history_sorts_by_coins_per_hour(auth_client, player) -> None:
    """Coins/hour sorting orders rows using the analysis-derived metric."""

    ingest_battle_report(
        "\n".join(
            [
                "Battle Report",
                "Battle Date: 2025-12-01 13:45:00",
                "Tier: 6",
                "Wave: 111",
                "Real Time: 1h 0m 0s",
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
                "Tier: 6",
                "Wave: 222",
                "Real Time: 4h 0m 0s",
                "Coins Earned: 2.00M",
            ]
        ),
        player=player,
    )

    response = auth_client.get(reverse("core:battle_history"), data={"sort": "-coins_per_hour"})
    assert response.status_code == 200

    waves = [row["run"].run_progress.wave for row in response.context["page_rows"]]
    assert waves[:2] == [111, 222]


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
        data={"raw_text": raw_text, "is_tournament": "on", "tournament_rank": "gold"},
        follow=True,
    )
    assert response.status_code == 200

    content = response.content.decode("utf-8")
    assert all((row["run"].run_progress.wave or 0) != 3656 for row in response.context["page_rows"])
    assert "Top 3 Tournament Logs" in content
    assert "3656" in content

    response = auth_client.get(reverse("core:battle_history"), {"include_tournaments": "on"})
    assert response.status_code == 200
    assert "3656" in response.content.decode("utf-8")


def _report(*, battle_date: str, tier: str, wave: int) -> str:
    """Return a minimal Battle Report string for Battle History summary tests."""

    return "\n".join(
        [
            "Battle Report",
            f"Battle Date: {battle_date}",
            f"Tier: {tier}",
            f"Wave: {wave}",
            "Real Time: 1h 0m 0s",
            "Killed By: Boss",
            "Coins Earned: 1.00M",
        ]
    )


@pytest.mark.django_db
def test_battle_history_renders_highest_wave_and_tournament_summaries(auth_client, player) -> None:
    """Battle History summaries ignore active filters and use manual tournament tagging."""

    ingest_battle_report(_report(battle_date="2025-12-01 10:00:00", tier="1", wave=100), player=player)
    ingest_battle_report(_report(battle_date="2025-12-02 10:00:00", tier="1", wave=200), player=player)
    ingest_battle_report(_report(battle_date="2025-12-03 10:00:00", tier="2", wave=150), player=player)
    ingest_battle_report(_report(battle_date="2025-12-04 10:00:00", tier="3+", wave=222), player=player)

    ingest_battle_report(
        _report(battle_date="2025-12-02 11:00:00", tier="1", wave=400),
        player=player,
        is_tournament=True,
    )
    ingest_battle_report(
        _report(battle_date="2025-12-01 11:00:00", tier="1", wave=400),
        player=player,
        is_tournament=True,
    )
    ingest_battle_report(
        _report(battle_date="2025-12-01 12:00:00", tier="1", wave=300),
        player=player,
        is_tournament=True,
    )
    ingest_battle_report(
        _report(battle_date="2025-12-03 12:00:00", tier="1", wave=200),
        player=player,
        is_tournament=True,
    )

    response = auth_client.get(reverse("core:battle_history"), data={"tier": 99})
    assert response.status_code == 200

    content = response.content.decode("utf-8")
    assert "No battle reports match the current filters" in content
    assert "Highest Wave by Tier" in content
    assert "Top 3 Tournament Logs" in content

    assert response.context["highest_wave_by_tier"] == [
        {"tier": 1, "highest_wave": 200},
        {"tier": 2, "highest_wave": 150},
    ]

    top_logs = response.context["top_tournament_logs"]
    assert [entry.wave for entry in top_logs] == [400, 400, 300]
    assert top_logs[0].battle_date is not None
    assert top_logs[1].battle_date is not None
    assert top_logs[0].battle_date > top_logs[1].battle_date

    highest_wave_segment = re.search(
        r"Highest Wave by Tier.*?</table>",
        content,
        flags=re.DOTALL,
    )
    assert highest_wave_segment is not None
    assert "200" in highest_wave_segment.group(0)
    assert "400" not in highest_wave_segment.group(0)

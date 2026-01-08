import pytest

from core.services import ingest_battle_report
from definitions.models import BotDefinition
from gamedata.models import RunBot


@pytest.mark.integration
@pytest.mark.regression
@pytest.mark.django_db
def test_ingest_battle_report_creates_run_bot_rows(player) -> None:
    """Persist run bot usage rows from Battle Report bot lines."""

    flame_bot = BotDefinition.objects.create(name="Flame Bot", slug="flame_bot")
    golden_bot = BotDefinition.objects.create(name="Golden Bot", slug="golden_bot")

    raw_text = "\n".join(
        [
            "Battle Report",
            "Battle Date\tDec 14, 2025 01:39",
            "Wave\t121",
            "Bots",
            "Flame Bot Damage\t111.15B",
            "Golden Bot Coins Earned\t578",
            "",
        ]
    )

    report, _ = ingest_battle_report(raw_text, player=player)

    rows = RunBot.objects.filter(battle_report=report).order_by("bot_definition_id")
    assert list(rows.values_list("bot_definition_id", flat=True)) == [
        flame_bot.id,
        golden_bot.id,
    ]

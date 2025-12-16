"""Enforcement tests for the Prompt11/Prompt12 layered architecture."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from core.wiki_ingestion import ingest_wiki_rows, make_entity_id, scrape_leveled_entity_rows
from definitions.models import (
    BotDefinition,
    BotParameterDefinition,
    BotParameterLevel,
    CardDefinition,
    Currency,
    GuardianChipDefinition,
    ParameterKey,
    UltimateWeaponDefinition,
)
from definitions.wiki_rebuild import (
    rebuild_bots_from_wikidata,
    rebuild_guardian_chips_from_wikidata,
    rebuild_ultimate_weapons_from_wikidata,
)
from gamedata.models import BattleReport, BattleReportProgress, RunBot, RunCombatUltimateWeapon, RunGuardian, RunUtilityUltimateWeapon
from player_state.models import (
    Player,
    PlayerBot,
    PlayerBotParameter,
    PlayerCard,
    PlayerGuardianChipParameter,
    PlayerUltimateWeaponParameter,
    Preset,
)


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _read_fixture(name: str) -> str:
    """Read a fixture file from tests/fixtures."""

    return (FIXTURES_DIR / name).read_text(encoding="utf-8", errors="ignore")


def _ingest_bot_page(*, fixture: str, display_name: str, parse_version: str = "bots_v1") -> None:
    """Ingest the first table from a bot page fixture into WikiData."""

    html = _read_fixture(fixture)
    entity_id = make_entity_id(display_name)
    scraped = scrape_leveled_entity_rows(
        html,
        table_index=0,
        entity_name=display_name,
        entity_id=entity_id,
        entity_field="Bot",
    )
    ingest_wiki_rows(
        scraped,
        page_url=f"https://example.test/wiki/{display_name}",
        source_section=f"bots_{entity_id}_table_0",
        parse_version=parse_version,
        write=True,
    )


def _ingest_uw_page(*, fixture: str, display_name: str, parse_version: str = "ultimate_weapons_v1") -> None:
    """Ingest the first upgrade-cost table from a UW page fixture into WikiData."""

    html = _read_fixture(fixture)
    entity_id = make_entity_id(display_name)
    scraped = scrape_leveled_entity_rows(
        html,
        table_index=0,
        entity_name=display_name,
        entity_id=entity_id,
        entity_field="Ultimate Weapon",
        add_level_if_missing=True,
        header_aliases={"Cooldown (s)": "Cooldown", "Cooldown(s)": "Cooldown"},
    )
    ingest_wiki_rows(
        scraped,
        page_url=f"https://example.test/wiki/{display_name}",
        source_section=f"ultimate_weapons_{entity_id}_table_0",
        parse_version=parse_version,
        write=True,
    )


def _ingest_guardian_page(*, fixture: str, parse_version: str = "guardian_chips_v1") -> None:
    """Ingest the 5 guardian chip upgrade tables from a Guardian page fixture."""

    html = _read_fixture(fixture)
    chips = {
        "Ally": 2,
        "Attack": 3,
        "Fetch": 5,
        "Bounty": 6,
        "Summon": 7,
    }
    for name, table_index in chips.items():
        entity_id = make_entity_id(name)
        scraped = scrape_leveled_entity_rows(
            html,
            table_index=table_index,
            entity_name=name,
            entity_id=entity_id,
            entity_field="Guardian",
            add_level_if_missing=True,
            header_aliases={
                "Cooldown (s)": "Cooldown",
                "Cooldown(s)": "Cooldown",
                "Max Recovey": "Max Recovery",
                "Max Recovery": "Max Recovery",
            },
        )
        ingest_wiki_rows(
            scraped,
            page_url="https://example.test/wiki/Guardian",
            source_section=f"guardian_chips_{entity_id}_table_{table_index}",
            parse_version=parse_version,
            write=True,
        )


@pytest.mark.django_db
def test_structural_separation_definitions_do_not_import_gamedata_or_player_state() -> None:
    """Definitions layer must not import GameData or Player State."""

    source = Path("definitions/models.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden = {"gamedata", "player_state"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] not in forbidden
        if isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".")[0] not in forbidden


@pytest.mark.django_db
def test_structural_separation_gamedata_does_not_import_parameter_level_tables() -> None:
    """GameData layer must not depend on ParameterLevel tables."""

    source = Path("gamedata/models.py").read_text(encoding="utf-8")
    assert "ParameterLevel" not in source
    assert "BotParameterLevel" not in source
    assert "UltimateWeaponParameterLevel" not in source
    assert "GuardianChipParameterLevel" not in source
    assert "PlayerBotParameter" not in source
    assert "PlayerUltimateWeaponParameter" not in source
    assert "PlayerGuardianChipParameter" not in source


@pytest.mark.django_db
def test_wiki_drift_counts_and_parameter_counts_match_prompt11() -> None:
    """Rebuild from fixtures and enforce entity/parameter counts."""

    _ingest_bot_page(fixture="wiki_bot_amplify_bot_v1.html", display_name="Amplify Bot")
    _ingest_bot_page(fixture="wiki_bot_flame_bot_v1.html", display_name="Flame Bot")
    _ingest_bot_page(fixture="wiki_bot_thunder_bot_v1.html", display_name="Thunder Bot")
    _ingest_bot_page(fixture="wiki_bot_golden_bot_v1.html", display_name="Golden Bot")

    for name, fixture in [
        ("Chain Lightning", "wiki_uw_chain_lightning_v1.html"),
        ("Death Wave", "wiki_uw_death_wave_v1.html"),
        ("Golden Tower", "wiki_uw_golden_tower_v1.html"),
        ("Spotlight", "wiki_uw_spotlight_v1.html"),
        ("Smart Missiles", "wiki_uw_smart_missiles_v1.html"),
        ("Chrono Field", "wiki_uw_chrono_field_v1.html"),
        ("Inner Land Mines", "wiki_uw_inner_land_mines_v1.html"),
        ("Poison Swamp", "wiki_uw_poison_swamp_v1.html"),
        ("Black Hole", "wiki_uw_black_hole_v1.html"),
    ]:
        _ingest_uw_page(fixture=fixture, display_name=name)

    _ingest_guardian_page(fixture="wiki_guardian_page_v1.html")

    rebuild_bots_from_wikidata(write=True)
    rebuild_ultimate_weapons_from_wikidata(write=True)
    rebuild_guardian_chips_from_wikidata(write=True)

    assert BotDefinition.objects.count() == 4
    assert UltimateWeaponDefinition.objects.count() == 9
    assert GuardianChipDefinition.objects.count() == 5

    for bot in BotDefinition.objects.all():
        assert bot.parameter_definitions.count() == 4
    for uw in UltimateWeaponDefinition.objects.all():
        assert uw.parameter_definitions.count() == 3
    for chip in GuardianChipDefinition.objects.all():
        assert chip.parameter_definitions.count() == 3

    # Cards: definitions only, no ParameterKey/parameter tables.
    assert not hasattr(CardDefinition, "parameter_definitions")


@pytest.mark.django_db
def test_parameter_key_field_is_enforced_by_choices() -> None:
    """Invalid ParameterKey values must be rejected."""

    bot = BotDefinition.objects.create(name="Test Bot", slug="test_bot")
    param = BotParameterDefinition(bot_definition=bot, key="not-a-key", display_name="Bad", unit_kind="count")
    with pytest.raises(ValidationError):
        param.full_clean()


@pytest.mark.django_db
def test_upgrade_table_levels_are_contiguous_and_currency_is_enforced() -> None:
    """Parameter levels are contiguous starting at 1 and currency is enforced."""

    _ingest_bot_page(fixture="wiki_bot_amplify_bot_v1.html", display_name="Amplify Bot")
    rebuild_bots_from_wikidata(write=True)

    for param_def in BotParameterDefinition.objects.all():
        levels = list(param_def.levels.order_by("level").values_list("level", flat=True))
        assert levels[0] == 1
        assert levels == list(range(1, max(levels) + 1))
        assert all(row.currency == Currency.MEDALS for row in param_def.levels.all())

    # DB constraint must reject wrong currency.
    one = BotParameterDefinition.objects.first()
    assert one is not None
    with pytest.raises(IntegrityError):
        BotParameterLevel.objects.create(
            parameter_definition=one,
            level=999,
            value_raw="0",
            cost_raw="0",
            currency=Currency.STONES,
        )


@pytest.mark.django_db
def test_card_enforcement_playercard_tracks_stars_only() -> None:
    """PlayerCard must only track stars_unlocked as functional progress."""

    assert hasattr(PlayerCard, "stars_unlocked")
    assert not hasattr(PlayerCard, "owned")
    assert not hasattr(PlayerCard, "level")
    assert not hasattr(PlayerCard, "star")


@pytest.mark.django_db
def test_player_parameter_integrity_unique_and_locked_prevents_upgrade() -> None:
    """PlayerParameter rows are unique and cannot be upgraded when locked."""

    bot_def = BotDefinition.objects.create(name="Amplify Bot", slug="amplify_bot")
    param_def = BotParameterDefinition.objects.create(
        bot_definition=bot_def, key=ParameterKey.COOLDOWN, display_name="Cooldown", unit_kind="seconds"
    )

    player = Player.objects.create(name="default")
    player_bot = PlayerBot.objects.create(player=player, bot_definition=bot_def, bot_slug=bot_def.slug, unlocked=False)

    locked = PlayerBotParameter(player_bot=player_bot, parameter_definition=param_def, level=1)
    with pytest.raises(ValidationError):
        locked.full_clean()

    player_bot.unlocked = True
    player_bot.save()
    ok = PlayerBotParameter.objects.create(player_bot=player_bot, parameter_definition=param_def, level=1)
    with pytest.raises((ValidationError, IntegrityError)):
        PlayerBotParameter.objects.create(player_bot=player_bot, parameter_definition=param_def, level=1)

    assert ok.level == 1


@pytest.mark.django_db
def test_gamedata_models_do_not_reference_player_parameter_tables() -> None:
    """run* models must not FK to player parameter tables."""

    forbidden = {PlayerBotParameter, PlayerUltimateWeaponParameter, PlayerGuardianChipParameter}
    for model in (RunBot, RunGuardian, RunCombatUltimateWeapon, RunUtilityUltimateWeapon):
        for field in model._meta.fields:
            rel = getattr(field, "remote_field", None)
            related = getattr(rel, "model", None)
            assert related not in forbidden


@pytest.mark.django_db
def test_preset_delete_does_not_delete_battle_reports() -> None:
    """Deleting a Preset must not delete BattleReport rows."""

    player = Player.objects.create(name="default")
    preset = Preset.objects.create(player=player, name="Farming")

    report = BattleReport.objects.create(raw_text="Battle Report\n", checksum="x" * 64)
    progress = BattleReportProgress.objects.create(
        battle_report=report,
        tier=1,
        wave=1,
        real_time_seconds=1,
        preset=preset,
    )
    preset.delete()
    progress.refresh_from_db()
    assert BattleReport.objects.filter(pk=report.pk).exists()
    assert progress.preset_id is None


@pytest.mark.django_db
def test_spotlight_placeholder_levels_are_omitted_and_max_levels_hold() -> None:
    """Spotlight placeholder/total rows are omitted from rebuilt parameter levels."""

    _ingest_uw_page(fixture="wiki_uw_spotlight_v1.html", display_name="Spotlight")
    rebuild_ultimate_weapons_from_wikidata(write=True)

    uw = UltimateWeaponDefinition.objects.get(slug="spotlight")
    defs = {param.key: param for param in uw.parameter_definitions.all()}

    quantity = defs["quantity"]
    assert quantity.levels.count() == 4
    assert quantity.levels.order_by("-level").first().level == 4

    angle = defs["angle"]
    assert angle.levels.filter(level=62).count() == 0

    coins_bonus = defs["coins_bonus"]
    assert coins_bonus.levels.order_by("-level").first().level == 26
    assert coins_bonus.levels.filter(level__gt=26).count() == 0


@pytest.mark.django_db
def test_guardian_placeholder_levels_are_omitted_on_rebuild() -> None:
    """Guardian chip rebuild omits placeholder/total parameter rows."""

    from core.wiki_ingestion import ScrapedWikiRow, compute_content_hash

    ingest_wiki_rows(
        [
            ScrapedWikiRow(
                canonical_name="Ally",
                entity_id="ally__level_1__star_none",
                raw_row={
                    "_wiki_entity_id": "ally",
                    "Guardian": "Ally",
                    "Level": "1",
                    "Recovery Amount": "10",
                    "Bits": "0",
                    "Cooldown": "5",
                    "Bits__2": "0",
                    "Max Recovery": "20",
                    "Bits__3": "0",
                },
                content_hash=compute_content_hash(
                    {
                        "_wiki_entity_id": "ally",
                        "Guardian": "Ally",
                        "Level": "1",
                        "Recovery Amount": "10",
                        "Bits": "0",
                        "Cooldown": "5",
                        "Bits__2": "0",
                        "Max Recovery": "20",
                        "Bits__3": "0",
                    }
                ),
            ),
            ScrapedWikiRow(
                canonical_name="Ally",
                entity_id="ally__level_62__star_none",
                raw_row={
                    "_wiki_entity_id": "ally",
                    "Guardian": "Ally",
                    "Level": "62",
                    "Recovery Amount": "-",
                    "Bits": "1000",
                    "Cooldown": "—",
                    "Bits__2": "1000",
                    "Max Recovery": "null",
                    "Bits__3": "1000",
                },
                content_hash=compute_content_hash(
                    {
                        "_wiki_entity_id": "ally",
                        "Guardian": "Ally",
                        "Level": "62",
                        "Recovery Amount": "-",
                        "Bits": "1000",
                        "Cooldown": "—",
                        "Bits__2": "1000",
                        "Max Recovery": "null",
                        "Bits__3": "1000",
                    }
                ),
            ),
        ],
        page_url="https://example.test/wiki/Guardian",
        source_section="guardian_chips_ally_table_2",
        parse_version="guardian_chips_v1",
        write=True,
    )

    rebuild_guardian_chips_from_wikidata(write=True)
    chip = GuardianChipDefinition.objects.get(slug="ally")
    assert chip.parameter_definitions.count() == 3
    for param_def in chip.parameter_definitions.all():
        assert param_def.levels.count() == 1
        assert param_def.levels.get().level == 1

"""Golden tests for Phase 4 parameterized effects across entity types.

These tests assert that:
- at least one real effect per entity type is computed deterministically,
- derived output changes when wiki revisions change,
- run data is not mutated by derived computations.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from analysis.engine import analyze_metric_series
from core.analysis_context import RevisionPolicy, build_player_context
from core.wiki_ingestion import compute_content_hash
from definitions.models import (
    BotDefinition,
    BotParameterDefinition,
    GuardianChipDefinition,
    GuardianChipParameterDefinition,
    ParameterKey,
    UltimateWeaponDefinition,
    UltimateWeaponParameterDefinition,
    WikiData,
)
from gamedata.models import BattleReport, BattleReportProgress
from player_state.models import (
    PlayerBot,
    PlayerBotParameter,
    PlayerGuardianChip,
    PlayerGuardianChipParameter,
    PlayerUltimateWeapon,
    PlayerUltimateWeaponParameter,
)


def _create_wikidata_level_row(
    *,
    parse_version: str,
    base_entity_id: str,
    entity_field: str,
    entity_name: str,
    level: int,
    last_seen: datetime,
    values: dict[str, str],
) -> WikiData:
    """Create a single leveled WikiData row matching scrape_leveled_entity_rows conventions."""

    raw_row: dict[str, str] = {
        "_wiki_entity_id": base_entity_id,
        entity_field: entity_name,
        "Level": str(level),
        **values,
    }
    return WikiData.objects.create(
        page_url=f"https://example.test/wiki/{base_entity_id}",
        canonical_name=entity_name,
        entity_id=f"{base_entity_id}__level_{level}__star_none",
        content_hash=compute_content_hash(raw_row),
        raw_row=raw_row,
        source_section="test",
        parse_version=parse_version,
        last_seen=last_seen,
    )


def _create_run(*, player, checksum: str = "r" * 64) -> BattleReport:
    """Create a minimal BattleReport + progress row for chartable analysis."""

    report = BattleReport.objects.create(
        player=player,
        raw_text="Battle Report\nCoins earned    1,200\n",
        checksum=checksum,
    )
    BattleReportProgress.objects.create(
        battle_report=report,
        player=player,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )
    return report


@pytest.mark.django_db
def test_golden_uw_uptime_percent_effect(player) -> None:
    """UW uptime% uses wiki Duration/Cooldown for the selected UW."""

    _create_wikidata_level_row(
        parse_version="ultimate_weapons_v1",
        base_entity_id="golden_tower",
        entity_field="Ultimate Weapon",
        entity_name="Golden Tower",
        level=1,
        last_seen=datetime(2025, 12, 1, tzinfo=timezone.utc),
        values={"Duration": "30", "Cooldown": "120"},
    )

    uw = UltimateWeaponDefinition.objects.create(name="Golden Tower", slug="golden_tower")
    duration = UltimateWeaponParameterDefinition.objects.create(
        ultimate_weapon_definition=uw,
        key=ParameterKey.DURATION,
        display_name="Duration",
        unit_kind="seconds",
    )
    cooldown = UltimateWeaponParameterDefinition.objects.create(
        ultimate_weapon_definition=uw,
        key=ParameterKey.COOLDOWN,
        display_name="Cooldown",
        unit_kind="seconds",
    )

    player_uw = PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=True,
    )
    PlayerUltimateWeaponParameter.objects.create(
        player=player,
        player_ultimate_weapon=player_uw,
        parameter_definition=duration,
        level=1,
    )
    PlayerUltimateWeaponParameter.objects.create(
        player=player,
        player_ultimate_weapon=player_uw,
        parameter_definition=cooldown,
        level=1,
    )

    report = _create_run(player=player, checksum="u" * 64)
    context = build_player_context(player=player, revision_policy=RevisionPolicy(mode="latest"))
    series = analyze_metric_series(
        [report],
        metric_key="uw_uptime_percent",
        context=context,
        entity_type="ultimate_weapon",
        entity_name="Golden Tower",
    )

    assert series.points[0].value == pytest.approx(25.0)
    assert {p.key for p in series.used_parameters} == {"duration", "cooldown"}


@pytest.mark.django_db
def test_golden_uw_effective_cooldown_seconds_effect(player) -> None:
    """UW effective cooldown uses wiki Cooldown for the selected UW."""

    _create_wikidata_level_row(
        parse_version="ultimate_weapons_v1",
        base_entity_id="golden_tower",
        entity_field="Ultimate Weapon",
        entity_name="Golden Tower",
        level=1,
        last_seen=datetime(2025, 12, 1, tzinfo=timezone.utc),
        values={"Cooldown": "120"},
    )

    uw = UltimateWeaponDefinition.objects.create(name="Golden Tower", slug="golden_tower")
    cooldown = UltimateWeaponParameterDefinition.objects.create(
        ultimate_weapon_definition=uw,
        key=ParameterKey.COOLDOWN,
        display_name="Cooldown",
        unit_kind="seconds",
    )

    player_uw = PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=True,
    )
    PlayerUltimateWeaponParameter.objects.create(
        player=player,
        player_ultimate_weapon=player_uw,
        parameter_definition=cooldown,
        level=1,
    )

    report = _create_run(player=player, checksum="c" * 64)
    context = build_player_context(player=player, revision_policy=RevisionPolicy(mode="latest"))
    series = analyze_metric_series(
        [report],
        metric_key="uw_effective_cooldown_seconds",
        context=context,
        entity_type="ultimate_weapon",
        entity_name="Golden Tower",
    )

    assert series.points[0].value == pytest.approx(120.0)
    assert len(series.used_parameters) == 1
    assert series.used_parameters[0].key == "cooldown"
    assert series.used_parameters[0].wiki_revision_id is not None


@pytest.mark.django_db
def test_golden_guardian_activations_per_minute_effect(player) -> None:
    """Guardian activations/min uses wiki Cooldown for the selected chip."""

    _create_wikidata_level_row(
        parse_version="guardian_chips_v1",
        base_entity_id="ally",
        entity_field="Guardian",
        entity_name="Ally",
        level=1,
        last_seen=datetime(2025, 12, 1, tzinfo=timezone.utc),
        values={"Cooldown": "90"},
    )

    chip = GuardianChipDefinition.objects.create(name="Ally", slug="ally")
    cooldown = GuardianChipParameterDefinition.objects.create(
        guardian_chip_definition=chip,
        key=ParameterKey.COOLDOWN,
        display_name="Cooldown",
        unit_kind="seconds",
    )

    player_chip = PlayerGuardianChip.objects.create(
        player=player,
        guardian_chip_definition=chip,
        guardian_chip_slug=chip.slug,
        unlocked=True,
    )
    PlayerGuardianChipParameter.objects.create(
        player=player,
        player_guardian_chip=player_chip, parameter_definition=cooldown, level=1
    )

    report = _create_run(player=player, checksum="g" * 64)
    context = build_player_context(player=player, revision_policy=RevisionPolicy(mode="latest"))
    series = analyze_metric_series(
        [report],
        metric_key="guardian_activations_per_minute",
        context=context,
        entity_type="guardian_chip",
        entity_name="Ally",
    )

    assert series.points[0].value == pytest.approx(60.0 / 90.0)
    assert len(series.used_parameters) == 1
    assert series.used_parameters[0].key == "cooldown"


@pytest.mark.django_db
def test_golden_bot_uptime_percent_effect(player) -> None:
    """Bot uptime% uses wiki Duration/Cooldown for the selected bot."""

    _create_wikidata_level_row(
        parse_version="bots_v1",
        base_entity_id="golden_bot",
        entity_field="Bot",
        entity_name="Golden Bot",
        level=1,
        last_seen=datetime(2025, 12, 1, tzinfo=timezone.utc),
        values={"Duration": "10", "Cooldown": "50"},
    )

    bot = BotDefinition.objects.create(name="Golden Bot", slug="golden_bot")
    duration = BotParameterDefinition.objects.create(
        bot_definition=bot,
        key=ParameterKey.DURATION,
        display_name="Duration",
        unit_kind="seconds",
    )
    cooldown = BotParameterDefinition.objects.create(
        bot_definition=bot,
        key=ParameterKey.COOLDOWN,
        display_name="Cooldown",
        unit_kind="seconds",
    )

    player_bot = PlayerBot.objects.create(player=player, bot_definition=bot, bot_slug=bot.slug, unlocked=True)
    PlayerBotParameter.objects.create(player=player, player_bot=player_bot, parameter_definition=duration, level=1)
    PlayerBotParameter.objects.create(player=player, player_bot=player_bot, parameter_definition=cooldown, level=1)

    report = _create_run(player=player, checksum="b" * 64)
    context = build_player_context(player=player, revision_policy=RevisionPolicy(mode="latest"))
    series = analyze_metric_series(
        [report],
        metric_key="bot_uptime_percent",
        context=context,
        entity_type="bot",
        entity_name="Golden Bot",
    )

    assert series.points[0].value == pytest.approx(20.0)
    assert {p.key for p in series.used_parameters} == {"duration", "cooldown"}


@pytest.mark.django_db
def test_revision_diff_changes_derived_output_without_mutating_runs(player) -> None:
    """Same run + different wiki revision produces different derived output."""

    _create_wikidata_level_row(
        parse_version="ultimate_weapons_v1",
        base_entity_id="golden_tower",
        entity_field="Ultimate Weapon",
        entity_name="Golden Tower",
        level=1,
        last_seen=datetime(2025, 12, 1, tzinfo=timezone.utc),
        values={"Duration": "30", "Cooldown": "120"},
    )
    _create_wikidata_level_row(
        parse_version="ultimate_weapons_v1",
        base_entity_id="golden_tower",
        entity_field="Ultimate Weapon",
        entity_name="Golden Tower",
        level=1,
        last_seen=datetime(2025, 12, 2, tzinfo=timezone.utc),
        values={"Duration": "30", "Cooldown": "100"},
    )

    uw = UltimateWeaponDefinition.objects.create(name="Golden Tower", slug="golden_tower")
    duration = UltimateWeaponParameterDefinition.objects.create(
        ultimate_weapon_definition=uw,
        key=ParameterKey.DURATION,
        display_name="Duration",
        unit_kind="seconds",
    )
    cooldown = UltimateWeaponParameterDefinition.objects.create(
        ultimate_weapon_definition=uw,
        key=ParameterKey.COOLDOWN,
        display_name="Cooldown",
        unit_kind="seconds",
    )

    player_uw = PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=True,
    )
    PlayerUltimateWeaponParameter.objects.create(
        player=player,
        player_ultimate_weapon=player_uw,
        parameter_definition=duration,
        level=1,
    )
    PlayerUltimateWeaponParameter.objects.create(
        player=player,
        player_ultimate_weapon=player_uw,
        parameter_definition=cooldown,
        level=1,
    )

    report = _create_run(player=player, checksum="d" * 64)
    progress = BattleReportProgress.objects.get(player=player, battle_report=report)
    original_wave = progress.wave

    early = build_player_context(
        player=player,
        revision_policy=RevisionPolicy(mode="as_of", as_of=datetime(2025, 12, 1, 12, tzinfo=timezone.utc))
    )
    late = build_player_context(
        player=player,
        revision_policy=RevisionPolicy(mode="as_of", as_of=datetime(2025, 12, 3, 12, tzinfo=timezone.utc))
    )
    series_early = analyze_metric_series(
        [report],
        metric_key="uw_uptime_percent",
        context=early,
        entity_type="ultimate_weapon",
        entity_name="Golden Tower",
    )
    series_late = analyze_metric_series(
        [report],
        metric_key="uw_uptime_percent",
        context=late,
        entity_type="ultimate_weapon",
        entity_name="Golden Tower",
    )

    assert series_early.points[0].value == pytest.approx(25.0)
    assert series_late.points[0].value == pytest.approx(30.0)

    progress.refresh_from_db()
    assert progress.wave == original_wave


@pytest.mark.django_db
def test_revision_diff_changes_effective_cooldown_seconds_across_wiki_revisions(player) -> None:
    """Same run + different wiki revision produces different effective cooldown output."""

    _create_wikidata_level_row(
        parse_version="ultimate_weapons_v1",
        base_entity_id="golden_tower",
        entity_field="Ultimate Weapon",
        entity_name="Golden Tower",
        level=1,
        last_seen=datetime(2025, 12, 1, tzinfo=timezone.utc),
        values={"Cooldown": "120"},
    )
    _create_wikidata_level_row(
        parse_version="ultimate_weapons_v1",
        base_entity_id="golden_tower",
        entity_field="Ultimate Weapon",
        entity_name="Golden Tower",
        level=1,
        last_seen=datetime(2025, 12, 2, tzinfo=timezone.utc),
        values={"Cooldown": "100"},
    )

    uw = UltimateWeaponDefinition.objects.create(name="Golden Tower", slug="golden_tower")
    cooldown = UltimateWeaponParameterDefinition.objects.create(
        ultimate_weapon_definition=uw,
        key=ParameterKey.COOLDOWN,
        display_name="Cooldown",
        unit_kind="seconds",
    )

    player_uw = PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=True,
    )
    PlayerUltimateWeaponParameter.objects.create(
        player=player,
        player_ultimate_weapon=player_uw,
        parameter_definition=cooldown,
        level=1,
    )

    report = _create_run(player=player, checksum="e" * 64)
    progress = BattleReportProgress.objects.get(player=player, battle_report=report)
    original_wave = progress.wave

    early = build_player_context(
        player=player,
        revision_policy=RevisionPolicy(mode="as_of", as_of=datetime(2025, 12, 1, 12, tzinfo=timezone.utc))
    )
    late = build_player_context(
        player=player,
        revision_policy=RevisionPolicy(mode="as_of", as_of=datetime(2025, 12, 3, 12, tzinfo=timezone.utc))
    )
    series_early = analyze_metric_series(
        [report],
        metric_key="uw_effective_cooldown_seconds",
        context=early,
        entity_type="ultimate_weapon",
        entity_name="Golden Tower",
    )
    series_late = analyze_metric_series(
        [report],
        metric_key="uw_effective_cooldown_seconds",
        context=late,
        entity_type="ultimate_weapon",
        entity_name="Golden Tower",
    )

    assert series_early.points[0].value == pytest.approx(120.0)
    assert series_late.points[0].value == pytest.approx(100.0)
    assert series_early.used_parameters[0].wiki_revision_id != series_late.used_parameters[0].wiki_revision_id

    progress.refresh_from_db()
    assert progress.wave == original_wave

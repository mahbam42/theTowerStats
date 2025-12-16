"""Tests for Phase 4 derived metrics + revision-aware parameter selection.

Phase 4 requires that wiki-derived parameter values can safely drive derived
metrics across revisions without mutating stored run data.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from analysis.engine import analyze_metric_series
from core.analysis_context import RevisionPolicy, build_player_context
from core.wiki_ingestion import compute_content_hash
from definitions.models import ParameterKey, UltimateWeaponDefinition, UltimateWeaponParameterDefinition, WikiData
from gamedata.models import BattleReport, BattleReportProgress
from player_state.models import Player, PlayerUltimateWeapon, PlayerUltimateWeaponParameter


@pytest.mark.django_db
def test_build_player_context_includes_selected_parameter_levels() -> None:
    """Player context DTO includes selected parameter-level values for unlocked entities."""

    wiki_row = {
        "_wiki_entity_id": "golden_tower",
        "Ultimate Weapon": "Golden Tower",
        "Level": "1",
        "Cooldown": "100",
    }
    wiki = WikiData.objects.create(
        page_url="https://example.test/wiki/Golden_Tower",
        canonical_name="Golden Tower",
        entity_id="golden_tower__level_1__star_none",
        content_hash=compute_content_hash(wiki_row),
        raw_row=wiki_row,
        source_section="ultimate_weapons_golden_tower_table_0",
        parse_version="ultimate_weapons_v1",
        last_seen=datetime(2025, 12, 1, tzinfo=timezone.utc),
    )

    uw = UltimateWeaponDefinition.objects.create(name="Golden Tower", slug="golden_tower", source_wikidata=wiki)
    cooldown = UltimateWeaponParameterDefinition.objects.create(
        ultimate_weapon_definition=uw,
        key=ParameterKey.COOLDOWN,
        display_name="Cooldown",
        unit_kind="seconds",
    )

    player = Player.objects.create(name="default")
    player_uw = PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=uw,
        ultimate_weapon_slug=uw.slug,
        unlocked=True,
    )
    PlayerUltimateWeaponParameter.objects.create(
        player_ultimate_weapon=player_uw, parameter_definition=cooldown, level=1
    )

    context = build_player_context(revision_policy=RevisionPolicy(mode="latest"))
    assert context.ultimate_weapons
    assert context.ultimate_weapons[0].unlocked is True
    assert context.ultimate_weapons[0].parameters
    assert context.ultimate_weapons[0].parameters[0].key == ParameterKey.COOLDOWN
    assert context.ultimate_weapons[0].parameters[0].wiki_revision_id == wiki.id


@pytest.mark.django_db
def test_derived_metric_returns_none_without_entity_selection() -> None:
    """Entity-scoped derived metrics remain defensive when selection is missing."""

    report = BattleReport.objects.create(raw_text="Battle Report\nCoins earned    1,200\n", checksum="d" * 64)
    BattleReportProgress.objects.create(
        battle_report=report,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    context = build_player_context(revision_policy=RevisionPolicy(mode="latest"))
    series = analyze_metric_series(
        [report],
        metric_key="uw_uptime_percent",
        context=context,
        entity_type="ultimate_weapon",
        entity_name=None,
    )
    assert len(series.points) == 1
    assert series.points[0].value is None

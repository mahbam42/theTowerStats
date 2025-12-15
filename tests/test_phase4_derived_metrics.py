"""Tests for Phase 4 derived metrics wiring after Prompt12 refactor.

Prompt12 restructures wiki definitions and removes card parameter tables.
Derived metrics remain defensive: they must not raise when context is missing
or incomplete.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from analysis.engine import analyze_metric_series
from core.analysis_context import RevisionPolicy, build_player_context
from definitions.models import (
    Currency,
    ParameterKey,
    UltimateWeaponDefinition,
    UltimateWeaponParameterDefinition,
    UltimateWeaponParameterLevel,
    Unit,
    WikiData,
)
from gamedata.models import BattleReport, BattleReportProgress
from player_state.models import Player, PlayerUltimateWeapon, PlayerUltimateWeaponParameter


@pytest.mark.django_db
def test_build_player_context_includes_selected_parameter_levels() -> None:
    """Player context DTO includes selected parameter-level values for unlocked entities."""

    wiki = WikiData.objects.create(
        page_url="https://example.test/wiki",
        canonical_name="Golden Tower",
        entity_id="golden_tower",
        content_hash="x" * 64,
        raw_row={"Name": "Golden Tower"},
        source_section="test",
        parse_version="test_v1",
    )
    Unit.objects.get_or_create(name="seconds", defaults={"symbol": "s", "kind": Unit.Kind.SECONDS})

    uw = UltimateWeaponDefinition.objects.create(name="Golden Tower", slug="golden_tower", source_wikidata=wiki)
    cooldown = UltimateWeaponParameterDefinition.objects.create(
        ultimate_weapon_definition=uw,
        key=ParameterKey.COOLDOWN,
        display_name="Cooldown",
        unit_kind=Unit.Kind.SECONDS,
    )
    UltimateWeaponParameterLevel.objects.create(
        parameter_definition=cooldown,
        level=1,
        value_raw="100",
        cost_raw="5",
        currency=Currency.STONES,
        source_wikidata=wiki,
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


@pytest.mark.django_db
def test_derived_metric_returns_none_without_required_context_keys() -> None:
    """Derived metric computation stays defensive even when context keys differ."""

    report = BattleReport.objects.create(raw_text="Battle Report\nCoins earned    1,200\n", checksum="d" * 64)
    BattleReportProgress.objects.create(
        battle_report=report,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    context = build_player_context(revision_policy=RevisionPolicy(mode="latest"))
    series = analyze_metric_series([report], metric_key="effective_cooldown_seconds", context=context)
    assert len(series.points) == 1
    assert series.points[0].value is None


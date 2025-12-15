"""Tests for Phase 4 derived metrics (parameterized mechanics)."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from analysis.engine import analyze_metric_series
from core.analysis_context import RevisionPolicy, build_player_context
from core.models import (
    BotDefinition,
    BotLevel,
    BotParameter,
    CardDefinition,
    CardLevel,
    CardParameter,
    GameData,
    GuardianChipDefinition,
    GuardianChipLevel,
    GuardianChipParameter,
    PlayerBot,
    PlayerCard,
    PlayerGuardianChip,
    PlayerUltimateWeapon,
    RunProgress,
    UltimateWeaponDefinition,
    UltimateWeaponLevel,
    UltimateWeaponParameter,
    WikiData,
)


def _wikidata_revision(*, entity_name: str, content_hash: str, last_seen: datetime) -> WikiData:
    """Create a minimal WikiData revision for tests."""

    return WikiData.objects.create(
        page_url="https://example.test/wiki",
        canonical_name=entity_name,
        entity_id=entity_name.casefold().replace(" ", "_"),
        content_hash=content_hash,
        raw_row={"Name": entity_name, "hash": content_hash},
        source_section="test",
        last_seen=last_seen,
        parse_version="test_v1",
    )


@pytest.mark.django_db
def test_effective_cooldown_golden() -> None:
    """Compute effective cooldown with additive reductions (golden)."""

    run = GameData.objects.create(raw_text="Battle Report\nCoins earned    1,200\n", checksum="cd" * 32)
    RunProgress.objects.create(
        game_data=run,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    PlayerUltimateWeapon.objects.create(weapon_name="Golden Tower", unlocked=True)
    rev = _wikidata_revision(
        entity_name="Golden Tower",
        content_hash="uw1",
        last_seen=datetime(2025, 12, 1, tzinfo=timezone.utc),
    )
    uw_def = UltimateWeaponDefinition.objects.create(name="Golden Tower")
    uw_level = UltimateWeaponLevel.objects.create(
        ultimate_weapon_definition=uw_def, level=1, raw_row={}, source_wikidata=rev
    )
    UltimateWeaponParameter.objects.create(
        ultimate_weapon_definition=uw_def,
        ultimate_weapon_level=uw_level,
        key="base_cooldown_seconds",
        raw_value="100",
        source_wikidata=rev,
    )

    card_def = CardDefinition.objects.create(name="Cooldown Card")
    card_level = CardLevel.objects.create(card_definition=card_def, level=1, raw_row={}, source_wikidata=rev)
    PlayerCard.objects.create(card_definition=card_def, owned=True, level=1)
    CardParameter.objects.create(
        card_definition=card_def,
        card_level=card_level,
        key="cooldown_reduction_percent",
        raw_value="10%",
        source_wikidata=rev,
    )
    CardParameter.objects.create(
        card_definition=card_def,
        card_level=card_level,
        key="cooldown_reduction_percent",
        raw_value="5%",
        source_wikidata=rev,
    )

    context = build_player_context(revision_policy=RevisionPolicy(mode="latest"))
    series = analyze_metric_series([run], metric_key="effective_cooldown_seconds", context=context)
    assert len(series.points) == 1
    assert series.points[0].value == 85.0


@pytest.mark.django_db
def test_ev_simulated_golden_seeded() -> None:
    """Compute seeded Monte Carlo EV multiplier (golden)."""

    run = GameData.objects.create(raw_text="Battle Report\nCoins earned    1,200\n", checksum="ev" * 32)
    RunProgress.objects.create(
        game_data=run,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    card_def = CardDefinition.objects.create(name="Proc Card")
    card_level = CardLevel.objects.create(card_definition=card_def, level=1, raw_row={})
    PlayerCard.objects.create(card_definition=card_def, owned=True, level=1)
    rev = _wikidata_revision(
        entity_name="Proc Card",
        content_hash="card1",
        last_seen=datetime(2025, 12, 1, tzinfo=timezone.utc),
    )
    CardParameter.objects.create(
        card_definition=card_def,
        card_level=card_level,
        key="proc_chance",
        raw_value="25%",
        source_wikidata=rev,
    )
    CardParameter.objects.create(
        card_definition=card_def,
        card_level=card_level,
        key="proc_multiplier",
        raw_value="x2",
        source_wikidata=rev,
    )

    context = build_player_context(revision_policy=RevisionPolicy(mode="latest"))
    series = analyze_metric_series(
        [run],
        metric_key="coins_per_hour_ev_simulated",
        context=context,
        monte_carlo_trials=1000,
        monte_carlo_seed=123,
    )
    assert len(series.points) == 1
    observed = 7200.0
    assert series.metric.key == "coins_per_hour_ev_simulated"
    assert series.points[0].value == pytest.approx(observed * 1.268, rel=0, abs=1e-9)


@pytest.mark.django_db
def test_parameter_revision_override_is_respected_for_cards() -> None:
    """Select an older revision explicitly and keep results stable."""

    run = GameData.objects.create(raw_text="Battle Report\nCoins earned    1,200\n", checksum="rev" * 21 + "x" * 22)
    RunProgress.objects.create(
        game_data=run,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    card_def = CardDefinition.objects.create(name="Coin Bonus")
    card_level = CardLevel.objects.create(card_definition=card_def, level=1, raw_row={})
    PlayerCard.objects.create(card_definition=card_def, owned=True, level=1)

    rev_old = _wikidata_revision(
        entity_name="Coin Bonus",
        content_hash="old",
        last_seen=datetime(2025, 12, 1, tzinfo=timezone.utc),
    )
    CardParameter.objects.create(
        card_definition=card_def,
        card_level=card_level,
        key="coins_multiplier",
        raw_value="x1.10",
        source_wikidata=rev_old,
    )

    rev_new = _wikidata_revision(
        entity_name="Coin Bonus",
        content_hash="new",
        last_seen=datetime(2025, 12, 2, tzinfo=timezone.utc),
    )
    CardParameter.objects.create(
        card_definition=card_def,
        card_level=card_level,
        key="coins_multiplier",
        raw_value="x1.20",
        source_wikidata=rev_new,
    )

    context_old = build_player_context(
        revision_policy=RevisionPolicy(overrides={("card", "Coin Bonus"): rev_old.pk})
    )
    series_old = analyze_metric_series(
        [run],
        metric_key="coins_per_hour_effective_multiplier",
        context=context_old,
    )
    assert series_old.points[0].value == 7200.0 * 1.10

    context_latest = build_player_context(revision_policy=RevisionPolicy(mode="latest"))
    series_latest = analyze_metric_series(
        [run],
        metric_key="coins_per_hour_effective_multiplier",
        context=context_latest,
    )
    assert series_latest.points[0].value == 7200.0 * 1.20


@pytest.mark.django_db
def test_missing_context_returns_partial_results_without_raising() -> None:
    """Derived metrics return None values when required context is missing."""

    run = GameData.objects.create(raw_text="Battle Report\nCoins earned    1,200\n", checksum="missing" * 10 + "x" * 4)
    RunProgress.objects.create(
        game_data=run,
        battle_date=datetime(2025, 12, 1, tzinfo=timezone.utc),
        tier=1,
        wave=100,
        real_time_seconds=600,
    )

    series = analyze_metric_series([run], metric_key="coins_per_hour_effective_multiplier", context=None)
    assert len(series.points) == 1
    assert series.points[0].value is None


@pytest.mark.django_db
def test_revision_policy_latest_and_overrides_select_parameter_rows_across_entities() -> None:
    """Select revisions explicitly for each parameter table type."""

    bot = PlayerBot.objects.create(bot_name="Coin Bot", unlocked=True, level=1)
    chip = PlayerGuardianChip.objects.create(chip_name="Lucky Chip", owned=True, level=1)
    uw = PlayerUltimateWeapon.objects.create(weapon_name="Golden Tower", unlocked=True, level=1)

    bot_def = BotDefinition.objects.create(name=bot.bot_name)
    bot_level = BotLevel.objects.create(bot_definition=bot_def, level=1, raw_row={})
    chip_def = GuardianChipDefinition.objects.create(name=chip.chip_name)
    chip_level = GuardianChipLevel.objects.create(guardian_chip_definition=chip_def, level=1, raw_row={})
    uw_def = UltimateWeaponDefinition.objects.create(name=uw.weapon_name)
    uw_level = UltimateWeaponLevel.objects.create(ultimate_weapon_definition=uw_def, level=1, raw_row={})

    old = _wikidata_revision(
        entity_name="old",
        content_hash="old_all",
        last_seen=datetime(2025, 12, 1, tzinfo=timezone.utc),
    )
    new = _wikidata_revision(
        entity_name="new",
        content_hash="new_all",
        last_seen=datetime(2025, 12, 2, tzinfo=timezone.utc),
    )

    BotParameter.objects.create(
        bot_definition=bot_def,
        bot_level=bot_level,
        key="coins_multiplier_old",
        raw_value="x1.05",
        source_wikidata=old,
    )
    BotParameter.objects.create(
        bot_definition=bot_def,
        bot_level=bot_level,
        key="coins_multiplier_new",
        raw_value="x1.10",
        source_wikidata=new,
    )
    GuardianChipParameter.objects.create(
        guardian_chip_definition=chip_def,
        guardian_chip_level=chip_level,
        key="coins_multiplier_old",
        raw_value="x1.02",
        source_wikidata=old,
    )
    GuardianChipParameter.objects.create(
        guardian_chip_definition=chip_def,
        guardian_chip_level=chip_level,
        key="coins_multiplier_new",
        raw_value="x1.03",
        source_wikidata=new,
    )
    UltimateWeaponParameter.objects.create(
        ultimate_weapon_definition=uw_def,
        ultimate_weapon_level=uw_level,
        key="base_cooldown_seconds_old",
        raw_value="100",
        source_wikidata=old,
    )
    UltimateWeaponParameter.objects.create(
        ultimate_weapon_definition=uw_def,
        ultimate_weapon_level=uw_level,
        key="base_cooldown_seconds_new",
        raw_value="90",
        source_wikidata=new,
    )

    latest = build_player_context(revision_policy=RevisionPolicy(mode="latest"))
    latest_uw = next(item for item in latest.ultimate_weapons if item.name == uw.weapon_name)
    assert latest_uw.parameters[0].wiki_revision_id == new.pk

    overrides = build_player_context(
        revision_policy=RevisionPolicy(
            overrides={
                ("bot", bot.bot_name): old.pk,
                ("guardian_chip", chip.chip_name): old.pk,
                ("ultimate_weapon", uw.weapon_name): old.pk,
            }
        )
    )
    override_bot = next(item for item in overrides.bots if item.name == bot.bot_name)
    override_chip = next(item for item in overrides.guardian_chips if item.name == chip.chip_name)
    override_uw = next(item for item in overrides.ultimate_weapons if item.name == uw.weapon_name)
    assert all(param.wiki_revision_id == old.pk for param in override_bot.parameters)
    assert all(param.wiki_revision_id == old.pk for param in override_chip.parameters)
    assert all(param.wiki_revision_id == old.pk for param in override_uw.parameters)

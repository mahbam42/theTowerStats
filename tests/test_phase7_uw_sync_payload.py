"""Phase 7 UW sync payload integration tests."""

from __future__ import annotations

import pytest
from typing import cast


@pytest.mark.django_db
def test_uw_sync_payload_includes_golden_bot_and_overlap_windows(player) -> None:
    """Include Golden Bot timing when available and emit overlap windows for band rendering."""

    from core.uw_sync import build_uw_sync_payload
    from definitions.models import BotDefinition, BotParameterDefinition, ParameterKey, UltimateWeaponDefinition, UltimateWeaponParameterDefinition, Unit
    from player_state.models import PlayerBot, PlayerBotParameter, PlayerUltimateWeapon, PlayerUltimateWeaponParameter

    golden_bot = BotDefinition.objects.create(name="Golden Bot", slug="golden_bot")
    bot_cd = BotParameterDefinition.objects.create(
        bot_definition=golden_bot,
        key=ParameterKey.COOLDOWN.value,
        display_name="Cooldown",
        unit_kind=Unit.Kind.SECONDS,
    )
    bot_dur = BotParameterDefinition.objects.create(
        bot_definition=golden_bot,
        key=ParameterKey.DURATION.value,
        display_name="Duration",
        unit_kind=Unit.Kind.SECONDS,
    )
    player_bot = PlayerBot.objects.create(player=player, bot_definition=golden_bot, bot_slug="golden_bot", unlocked=True)
    PlayerBotParameter.objects.create(
        player=player,
        player_bot=player_bot,
        parameter_definition=bot_cd,
        level=1,
        effective_value_raw="10",
    )
    PlayerBotParameter.objects.create(
        player=player,
        player_bot=player_bot,
        parameter_definition=bot_dur,
        level=1,
        effective_value_raw="5",
    )

    for slug, name in (("golden_tower", "Golden Tower"), ("black_hole", "Black Hole"), ("death_wave", "Death Wave")):
        uw_def = UltimateWeaponDefinition.objects.create(name=name, slug=slug)
        uw_cd = UltimateWeaponParameterDefinition.objects.create(
            ultimate_weapon_definition=uw_def,
            key=ParameterKey.COOLDOWN.value,
            display_name="Cooldown",
            unit_kind=Unit.Kind.SECONDS,
        )
        uw_dur = UltimateWeaponParameterDefinition.objects.create(
            ultimate_weapon_definition=uw_def,
            key=ParameterKey.DURATION.value,
            display_name="Duration",
            unit_kind=Unit.Kind.SECONDS,
        )
        player_uw = PlayerUltimateWeapon.objects.create(
            player=player,
            ultimate_weapon_definition=uw_def,
            ultimate_weapon_slug=slug,
            unlocked=True,
        )
        PlayerUltimateWeaponParameter.objects.create(
            player=player,
            player_ultimate_weapon=player_uw,
            parameter_definition=uw_cd,
            level=1,
            effective_value_raw="10",
        )
        PlayerUltimateWeaponParameter.objects.create(
            player=player,
            player_ultimate_weapon=player_uw,
            parameter_definition=uw_dur,
            level=1,
            effective_value_raw="5",
        )

    payload = build_uw_sync_payload(player=player)
    assert payload is not None
    assert payload.summary["includes_golden_bot"] is True

    chart_data = cast(dict[str, object], payload.chart_data)
    datasets = cast(list[dict[str, object]], chart_data["datasets"])
    labels = {str(d.get("label")) for d in datasets}
    assert "Golden Bot" in labels
    assert "All overlap" in labels
    assert "Cumulative overlap %" in labels

    overlap_windows = cast(list[dict[str, str]], chart_data["overlap_windows"])
    assert overlap_windows
    assert overlap_windows[0] == {"start": "0s", "end": "4s"}


@pytest.mark.django_db
def test_uw_sync_payload_allows_death_wave_without_duration(player) -> None:
    """Render the sync chart when Death Wave duration is not tracked."""

    from core.uw_sync import build_uw_sync_payload
    from definitions.models import ParameterKey, UltimateWeaponDefinition, UltimateWeaponParameterDefinition, Unit
    from player_state.models import PlayerUltimateWeapon, PlayerUltimateWeaponParameter

    for slug, name in (("golden_tower", "Golden Tower"), ("black_hole", "Black Hole")):
        uw_def = UltimateWeaponDefinition.objects.create(name=name, slug=slug)
        uw_cd = UltimateWeaponParameterDefinition.objects.create(
            ultimate_weapon_definition=uw_def,
            key=ParameterKey.COOLDOWN.value,
            display_name="Cooldown",
            unit_kind=Unit.Kind.SECONDS,
        )
        uw_dur = UltimateWeaponParameterDefinition.objects.create(
            ultimate_weapon_definition=uw_def,
            key=ParameterKey.DURATION.value,
            display_name="Duration",
            unit_kind=Unit.Kind.SECONDS,
        )
        player_uw = PlayerUltimateWeapon.objects.create(
            player=player,
            ultimate_weapon_definition=uw_def,
            ultimate_weapon_slug=slug,
            unlocked=True,
        )
        PlayerUltimateWeaponParameter.objects.create(
            player=player,
            player_ultimate_weapon=player_uw,
            parameter_definition=uw_cd,
            level=1,
            effective_value_raw="10",
        )
        PlayerUltimateWeaponParameter.objects.create(
            player=player,
            player_ultimate_weapon=player_uw,
            parameter_definition=uw_dur,
            level=1,
            effective_value_raw="5",
        )

    death_wave_def = UltimateWeaponDefinition.objects.create(name="Death Wave", slug="death_wave")
    dw_cd = UltimateWeaponParameterDefinition.objects.create(
        ultimate_weapon_definition=death_wave_def,
        key=ParameterKey.COOLDOWN.value,
        display_name="Cooldown",
        unit_kind=Unit.Kind.SECONDS,
    )
    player_dw = PlayerUltimateWeapon.objects.create(
        player=player,
        ultimate_weapon_definition=death_wave_def,
        ultimate_weapon_slug="death_wave",
        unlocked=True,
    )
    PlayerUltimateWeaponParameter.objects.create(
        player=player,
        player_ultimate_weapon=player_dw,
        parameter_definition=dw_cd,
        level=1,
        effective_value_raw="10",
    )

    payload = build_uw_sync_payload(player=player)
    assert payload is not None
    overlap_windows = cast(list[dict[str, str]], cast(dict[str, object], payload.chart_data)["overlap_windows"])
    assert overlap_windows == [{"start": "0s", "end": "0s"}, {"start": "10s", "end": "10s"}]

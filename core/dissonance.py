"""Helpers for Dissonance run classification and progression tracking."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import math

from gamedata.models import BattleReportProgress, DISSONANCE_TYPE_KEYS, PlayerDissonanceTierBoost
from player_state.models import Player


DEFAULT_DISSONANCE_LEVEL = 1


def default_dissonance_levels() -> dict[str, int]:
    """Return the default per-type Dissonance level mapping.

    Returns:
        Dict keyed by Dissonance type with the baseline level for types that
        have not yet been unlocked by the player.
    """

    return {key: DEFAULT_DISSONANCE_LEVEL for key in DISSONANCE_TYPE_KEYS}


def next_dissonance_level(previous_level: int | None) -> int:
    """Return the next unlocked Dissonance level for one tier/type track.

    Args:
        previous_level: Previously unlocked level for the tier/type, or None
            when the player has no prior logged clear for that track.

    Returns:
        The next unlocked in-game Dissonance level. The first logged clear
        starts at level 3 to match the game's displayed multiplier progression.
    """

    baseline = max(int(previous_level or DEFAULT_DISSONANCE_LEVEL), DEFAULT_DISSONANCE_LEVEL)
    if baseline <= DEFAULT_DISSONANCE_LEVEL:
        return DEFAULT_DISSONANCE_LEVEL + 2
    return baseline + 1


def level_snapshot_for_tier(*, player: Player, tier: int | None) -> dict[str, int]:
    """Return the stored Dissonance levels for a player's tier.

    Args:
        player: Owning player.
        tier: Tier to inspect.

    Returns:
        Dict keyed by Dissonance type. Missing tiers return the default level
        mapping with level `1` for every type.
    """

    levels = default_dissonance_levels()
    if tier is None:
        return levels
    boosts = PlayerDissonanceTierBoost.objects.filter(player=player, tier=tier)
    for boost in boosts:
        levels[str(boost.dissonance_type)] = int(boost.current_level)
    return levels


def effective_multiplier(*, multiplier_level: int | float | Decimal | None, wave: int | None) -> Decimal:
    """Calculate the effective Dissonance multiplier for a wave.

    Args:
        multiplier_level: Current unlocked Dissonance level for the type.
        wave: Wave reached on the run.

    Returns:
        Decimal multiplier rounded to four decimal places.
    """

    level = Decimal(str(multiplier_level or DEFAULT_DISSONANCE_LEVEL))
    wave_value = Decimal(str(max(int(wave or 0), 0)))
    if level <= 1 or wave_value <= 0:
        return Decimal("1.0000")
    ratio = float(wave_value / Decimal("5000"))
    computed = Decimal("1") + (level - Decimal("1")) * Decimal(str(math.pow(ratio, 1.75)))
    return computed.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)


def record_dissonance_unlock(
    *,
    player: Player,
    tier: int | None,
    dissonance_type: str | None,
    wave: int | None,
) -> PlayerDissonanceTierBoost | None:
    """Advance and persist Dissonance progression for a completed run.

    Args:
        player: Owning player.
        tier: Tier the Dissonance run was completed on.
        dissonance_type: Dissonance type selected for the run.
        wave: Wave reached by the run.

    Returns:
        Updated PlayerDissonanceTierBoost row, or None when the input does not
        describe a trackable Dissonance run.
    """

    if tier is None or not dissonance_type:
        return None
    boost, created = PlayerDissonanceTierBoost.objects.get_or_create(
        player=player,
        tier=tier,
        dissonance_type=dissonance_type,
        defaults={
            "current_level": DEFAULT_DISSONANCE_LEVEL,
            "highest_effective_multiplier": Decimal("1.0000"),
            "top_effective_multipliers": [],
        },
    )
    boost.current_level = next_dissonance_level(None if created else int(boost.current_level))
    multiplier = effective_multiplier(multiplier_level=boost.current_level, wave=wave)
    history = [
        float(value)
        for value in boost.top_effective_multipliers
        if isinstance(value, (int, float))
    ]
    history.append(float(multiplier))
    history = sorted(history, reverse=True)[:3]
    boost.top_effective_multipliers = history
    if multiplier > boost.highest_effective_multiplier:
        boost.highest_effective_multiplier = multiplier
    boost.save()
    return boost


def tier_bonus_rows(*, player: Player) -> list[dict[str, object]]:
    """Return tier/grouped Dissonance bonus rows for Battle History UI.

    Args:
        player: Owning player.

    Returns:
        List of dictionaries sorted by tier and Dissonance type for modal/table
        rendering.
    """

    boosts = PlayerDissonanceTierBoost.objects.filter(player=player).order_by("tier", "dissonance_type")
    rows: list[dict[str, object]] = []
    for boost in boosts:
        type_label = dict(boost._meta.get_field("dissonance_type").choices).get(
            str(boost.dissonance_type),
            str(boost.dissonance_type),
        )
        rows.append(
            {
                "tier": int(boost.tier),
                "dissonance_type": str(boost.dissonance_type),
                "dissonance_type_label": type_label,
                "current_level": int(boost.current_level),
                "highest_effective_multiplier": float(boost.highest_effective_multiplier),
                "top_effective_multipliers": tuple(boost.top_effective_multipliers),
            }
        )
    return rows


def rebuild_dissonance_progression(*, player: Player) -> None:
    """Recompute Dissonance snapshots and boost summaries for one player.

    Args:
        player: Owning player whose saved runs should be replayed in order.

    Returns:
        None.
    """

    PlayerDissonanceTierBoost.objects.filter(player=player).delete()

    progresses = (
        BattleReportProgress.objects.filter(player=player)
        .select_related("battle_report")
        .order_by("battle_date", "battle_report__parsed_at", "id")
    )
    levels_by_tier: dict[int, dict[str, int]] = {}
    boost_rows: dict[tuple[int, str], PlayerDissonanceTierBoost] = {}

    for progress in progresses:
        snapshot = default_dissonance_levels()
        if progress.tier is not None:
            snapshot.update(levels_by_tier.get(int(progress.tier), {}))
        if progress.dissonance_levels_snapshot != snapshot:
            BattleReportProgress.objects.filter(id=progress.id).update(
                dissonance_levels_snapshot=snapshot
            )

        if not progress.is_dissonance or progress.tier is None or not progress.dissonance_type:
            continue

        tier = int(progress.tier)
        dissonance_type = str(progress.dissonance_type)
        tier_levels = levels_by_tier.setdefault(tier, default_dissonance_levels())
        next_level = next_dissonance_level(tier_levels.get(dissonance_type))
        tier_levels[dissonance_type] = next_level

        multiplier = effective_multiplier(multiplier_level=next_level, wave=progress.wave)
        key = (tier, dissonance_type)
        row = boost_rows.get(key)
        if row is None:
            row = PlayerDissonanceTierBoost(
                player=player,
                tier=tier,
                dissonance_type=dissonance_type,
                current_level=next_level,
                highest_effective_multiplier=multiplier,
                top_effective_multipliers=[float(multiplier)],
            )
            boost_rows[key] = row
            continue

        row.current_level = next_level
        history = [
            float(value)
            for value in row.top_effective_multipliers
            if isinstance(value, (int, float))
        ]
        history.append(float(multiplier))
        row.top_effective_multipliers = sorted(history, reverse=True)[:3]
        if multiplier > row.highest_effective_multiplier:
            row.highest_effective_multiplier = multiplier

    if boost_rows:
        PlayerDissonanceTierBoost.objects.bulk_create(boost_rows.values())

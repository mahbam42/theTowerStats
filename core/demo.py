"""Demo mode helpers for safe, read-only exploration.

Demo mode allows an authenticated user to temporarily view a shared, seeded
dataset without affecting their own player-scoped data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.http import HttpRequest

from definitions.models import BotDefinition, CardDefinition, GuardianChipDefinition, UltimateWeaponDefinition
from gamedata.models import BattleReport
from player_state.models import Player, PlayerBot, PlayerCard, PlayerGuardianChip, PlayerUltimateWeapon

from core.parsers.battle_report import parse_battle_report
from core.services import ingest_battle_report

DEMO_SESSION_KEY: Final[str] = "tts_demo_mode"
DEMO_USERNAME: Final[str] = "__demo__"
DEMO_DISPLAY_NAME: Final[str] = "Demo Player"


@dataclass(frozen=True, slots=True)
class DemoSeedResult:
    """Outcome for demo dataset seeding."""

    seeded: bool
    imported_reports: int


def demo_mode_enabled(request: HttpRequest) -> bool:
    """Return True when demo mode is enabled for the current session."""

    return bool(getattr(request, "session", {}).get(DEMO_SESSION_KEY, False))


def set_demo_mode(request: HttpRequest, *, enabled: bool) -> None:
    """Enable or disable demo mode in the current session.

    Args:
        request: Incoming request whose session will be updated.
        enabled: Desired demo mode state.
    """

    request.session[DEMO_SESSION_KEY] = bool(enabled)
    request.session.modified = True


def get_demo_player() -> Player:
    """Return the shared demo Player, creating and seeding it when missing.

    Returns:
        The demo Player instance.
    """

    UserModel = get_user_model()
    demo_user: AbstractUser
    demo_user, created = UserModel.objects.get_or_create(username=DEMO_USERNAME)
    if created:
        demo_user.set_unusable_password()
        demo_user.save(update_fields=["password"])

    demo_player, _ = Player.objects.get_or_create(
        user=demo_user,
        defaults={"display_name": DEMO_DISPLAY_NAME},
    )
    seed_demo_player(demo_player)
    return demo_player


def seed_demo_player(player: Player) -> DemoSeedResult:
    """Seed demo battle reports and dashboards if the demo dataset is empty.

    Seeding is intentionally minimal and idempotent. It does not overwrite
    existing demo data in-place.

    Args:
        player: Demo Player record to populate.

    Returns:
        DemoSeedResult describing whether seeding occurred.
    """

    demo_reports = _demo_battle_reports()
    if not _should_reseed_demo_player(player, demo_reports):
        return DemoSeedResult(seeded=False, imported_reports=0)

    with transaction.atomic():
        BattleReport.objects.filter(player=player).delete()
        imported = 0
        for raw_text in demo_reports:
            _report, created = ingest_battle_report(raw_text, player=player, preset_name="Demo")
            imported += int(bool(created))

        _seed_demo_player_state(player)

    return DemoSeedResult(seeded=True, imported_reports=imported)


def _should_reseed_demo_player(player: Player, demo_reports: tuple[str, ...]) -> bool:
    """Return True when demo battle reports should be refreshed.

    Args:
        player: Demo Player record to inspect.
        demo_reports: Current demo seed payloads.

    Returns:
        True when the persisted demo data does not match the seed inputs.
    """

    existing = BattleReport.objects.filter(player=player)
    if not existing.exists():
        return True

    if existing.count() != len(demo_reports):
        return True

    expected_dates = {
        parsed.battle_date.date()
        for raw_text in demo_reports
        if (parsed := parse_battle_report(raw_text)).battle_date is not None
    }
    if not expected_dates:
        return False

    progress_dates = {
        progress.battle_date.date()
        for progress in player.battle_report_progress.exclude(battle_date__isnull=True)
    }
    return expected_dates != progress_dates


def _seed_demo_player_state(player: Player) -> None:
    """Seed basic player-state rows so read-only dashboards render in demo mode."""

    for definition in CardDefinition.objects.order_by("name"):
        PlayerCard.objects.get_or_create(
            player=player,
            card_slug=definition.slug,
            defaults={
                "card_definition": definition,
                "stars_unlocked": 1 if definition.rarity in ("Common", "Rare") else 0,
                "inventory_count": 0,
            },
        )

    for definition in UltimateWeaponDefinition.objects.order_by("name"):
        PlayerUltimateWeapon.objects.get_or_create(
            player=player,
            ultimate_weapon_slug=definition.slug,
            defaults={
                "ultimate_weapon_definition": definition,
                "unlocked": False,
            },
        )

    first_guardian = GuardianChipDefinition.objects.order_by("name").first()
    for definition in GuardianChipDefinition.objects.order_by("name"):
        PlayerGuardianChip.objects.get_or_create(
            player=player,
            guardian_chip_slug=definition.slug,
            defaults={
                "guardian_chip_definition": definition,
                "unlocked": bool(first_guardian and definition.slug == first_guardian.slug),
                "active": bool(first_guardian and definition.slug == first_guardian.slug),
            },
        )

    for definition in BotDefinition.objects.order_by("name"):
        PlayerBot.objects.get_or_create(
            player=player,
            bot_slug=definition.slug,
            defaults={
                "bot_definition": definition,
                "unlocked": False,
            },
        )


def _demo_battle_reports() -> tuple[str, ...]:
    """Return a small, deterministic set of demo Battle Report payloads."""

    return (
        "\n".join(
            [
                "Battle Report",
                "Battle Date\tNov 12, 2025 09:12",
                "Game Time\t1h 05m 15s",
                "Real Time\t10m 12s",
                "Tier\t1",
                "Wave\t63",
                "Killed By\tBoss",
                "Coins earned\t79.76K",
                "Cash earned\t$280.47K",
                "Interest earned\t$0",
                "Gem Blocks Tapped\t0",
                "Cells Earned\t0",
                "Reroll Shards Earned\t0",
                "Combat",
                "Damage dealt\t6.78M",
                "Enemies Destroyed",
                "Total Enemies\t45.46K",
                "Orb Kills\t294",
                "Death Ray Kills\t0",
                "Thorn damage\t0",
                "Utility",
                "Free Attack Upgrade\t0",
                "Free Defense Upgrade\t0",
                "Free Utility Upgrade\t0",
                "Waves Skipped\t0",
                "",
            ]
        ),
        "\n".join(
            [
                "Battle Report",
                "Battle Date\tDec 08, 2025 20:42",
                "Game Time\t1h 12m 42s",
                "Real Time\t11m 18s",
                "Tier\t2",
                "Wave\t71",
                "Killed By\tBoss",
                "Coins earned\t84.12K",
                "Cash earned\t$310.22K",
                "Interest earned\t$0",
                "Gem Blocks Tapped\t0",
                "Cells Earned\t0",
                "Reroll Shards Earned\t0",
                "Combat",
                "Damage dealt\t7.01M",
                "Enemies Destroyed",
                "Total Enemies\t48.90K",
                "Orb Kills\t312",
                "Death Ray Kills\t0",
                "Thorn damage\t0",
                "Utility",
                "Free Attack Upgrade\t0",
                "Free Defense Upgrade\t0",
                "Free Utility Upgrade\t0",
                "Waves Skipped\t0",
                "",
            ]
        ),
        "\n".join(
            [
                "Battle Report",
                "Battle Date\tDec 18, 2025 17:10",
                "Game Time\t9h 32m 8s",
                "Real Time\t2h 23m 4s",
                "Tier\t8",
                "Wave\t980",
                "Killed By\tBoss",
                "Coins earned\t21.54M",
                "Coins per hour\t9.03M",
                "Cash earned\t$80.70M",
                "Interest earned\t$1.96M",
                "Gem Blocks Tapped\t3",
                "Cells Earned\t133",
                "Reroll Shards Earned\t352",
                "Combat",
                "Damage dealt\t13.48q",
                "Damage Taken\t4.33B",
                "Damage Taken Wall\t1.07B",
                "Damage Taken While Berserked\t0",
                "Damage Gain From Berserk\tx0.00",
                "Death Defy\t0",
                "Lifesteal\t28.54M",
                "Projectiles Damage\t1.46q",
                "Projectiles Count\t184.61K",
                "Thorn damage\t5.50T",
                "Orb Damage\t352.41T",
                "Enemies Hit by Orbs\t864",
                "Land Mine Damage\t220.13T",
                "Land Mines Spawned\t18760",
                "Rend Armor Damage\t0",
                "Death Ray Damage\t0",
                "Smart Missile Damage\t32.40T",
                "Inner Land Mine Damage\t0",
                "Chain Lightning Damage\t11.37q",
                "Death Wave Damage\t3.85T",
                "Tagged by Deathwave\t4741",
                "Swamp Damage\t0",
                "Black Hole Damage\t2.66T",
                "Electrons Damage\t0",
                "Utility",
                "Waves Skipped\t0",
                "Recovery Packages\t390",
                "Free Attack Upgrade\t506",
                "Free Defense Upgrade\t492",
                "Free Utility Upgrade\t482",
                "HP From Death Wave\t0.00",
                "Coins From Death Wave\t119.28K",
                "Cash From Golden Tower\t$33.08M",
                "Coins From Golden Tower\t2.38M",
                "Coins From Black Hole\t0",
                "Coins From Spotlight\t44.52K",
                "Coins From Orb\t0",
                "Coins from Coin Upgrade\t7.83M",
                "Coins from Coin Bonuses\t10.86M",
                "Enemies Destroyed",
                "Total Enemies\t66205",
                "Basic\t41888",
                "Fast\t8542",
                "Tank\t8846",
                "Ranged\t6286",
                "Boss\t98",
                "Protector\t107",
                "Total Elites\t35",
                "Vampires\t11",
                "Rays\t10",
                "Scatters\t14",
                "Saboteur\t0",
                "Commander\t0",
                "Overcharge\t0",
                "Destroyed By Orbs\t864",
                "Destroyed by Thorns\t4",
                "Destroyed by Death Ray\t0",
                "Destroyed by Land Mine\t5721",
                "Destroyed in Spotlight\t6914",
                "Bots",
                "Flame Bot Damage\t26.02T",
                "Thunder Bot Stuns\t471",
                "Golden Bot Coins Earned\t18.89K",
                "Destroyed in Golden Bot\t516",
                "Guardian",
                "Damage\t5.25T",
                "Summoned enemies\t0",
                "Guardian coins stolen\t0",
                "Coins Fetched\t22.09K",
                "Gems\t3",
                "Medals\t1",
                "Reroll Shards\t27",
                "Cannon Shards\t6",
                "Armor Shards\t0",
                "Generator Shards\t0",
                "Core Shards\t3",
                "Common Modules\t0",
                "Rare Modules\t0",
                "",
            ]
        ),
        "\n".join(
            [
                "Battle Report",
                "Battle Date\tDec 20, 2025 15:24",
                "Game Time\t9h 18m 17s",
                "Real Time\t2h 19m 35s",
                "Tier\t8",
                "Wave\t958",
                "Killed By\tFast",
                "Coins earned\t15.83M",
                "Coins per hour\t6.81M",
                "Cash earned\t$33.31M",
                "Interest earned\t$1.91M",
                "Gem Blocks Tapped\t1",
                "Cells Earned\t108",
                "Reroll Shards Earned\t450",
                "Combat",
                "Damage dealt\t10.95q",
                "Damage Taken\t6.27B",
                "Damage Taken Wall\t1.06B",
                "Damage Taken While Berserked\t0",
                "Damage Gain From Berserk\tx0.00",
                "Death Defy\t0",
                "Lifesteal\t0",
                "Projectiles Damage\t695.69T",
                "Projectiles Count\t237.61K",
                "Thorn damage\t13.18T",
                "Orb Damage\t275.87T",
                "Enemies Hit by Orbs\t1.13K",
                "Land Mine Damage\t43.59T",
                "Land Mines Spawned\t19476",
                "Rend Armor Damage\t0",
                "Death Ray Damage\t3.47q",
                "Smart Missile Damage\t6.85T",
                "Inner Land Mine Damage\t0",
                "Chain Lightning Damage\t6.43q",
                "Death Wave Damage\t726.40B",
                "Tagged by Deathwave\t3543",
                "Swamp Damage\t0",
                "Black Hole Damage\t0",
                "Electrons Damage\t0",
                "Utility",
                "Waves Skipped\t0",
                "Recovery Packages\t573",
                "Free Attack Upgrade\t511",
                "Free Defense Upgrade\t468",
                "Free Utility Upgrade\t480",
                "HP From Death Wave\t38.00M",
                "Coins From Death Wave\t112.12K",
                "Cash From Golden Tower\t$14.67M",
                "Coins From Golden Tower\t2.56M",
                "Coins From Black Hole\t0",
                "Coins From Spotlight\t40.10K",
                "Coins From Orb\t0",
                "Coins from Coin Upgrade\t6.51M",
                "Coins from Coin Bonuses\t6.35M",
                "Enemies Destroyed",
                "Total Enemies\t64032",
                "Basic\t41059",
                "Fast\t8317",
                "Tank\t8293",
                "Ranged\t5921",
                "Boss\t95",
                "Protector\t107",
                "Total Elites\t30",
                "Vampires\t10",
                "Rays\t13",
                "Scatters\t7",
                "Saboteur\t0",
                "Commander\t0",
                "Overcharge\t0",
                "Destroyed By Orbs\t1127",
                "Destroyed by Thorns\t9",
                "Destroyed by Death Ray\t14297",
                "Destroyed by Land Mine\t1829",
                "Destroyed in Spotlight\t6733",
                "Bots",
                "Flame Bot Damage\t6.89T",
                "Thunder Bot Stuns\t586",
                "Golden Bot Coins Earned\t12.01K",
                "Destroyed in Golden Bot\t432",
                "Guardian",
                "Damage\t3.10T",
                "Summoned enemies\t0",
                "Guardian coins stolen\t0",
                "Coins Fetched\t12.52K",
                "Gems\t3",
                "Medals\t2",
                "Reroll Shards\t0",
                "Cannon Shards\t0",
                "Armor Shards\t6",
                "Generator Shards\t3",
                "Core Shards\t0",
                "Common Modules\t0",
                "Rare Modules\t0",
                "",
            ]
        ),
        "\n".join(
            [
                "Battle Report",
                "Battle Date\tDec 24, 2025 14:14",
                "Game Time\t21h 16m 16s",
                "Real Time\t4h 15m 26s",
                "Tier\t15",
                "Wave\t5170",
                "Killed By\tRay",
                "Coins earned\t3.55q",
                "Coins per hour\t834.45T",
                "Cash earned\t$131.86B",
                "Interest earned\t$7.63M",
                "Gem Blocks Tapped\t6",
                "Cells Earned\t413.62K",
                "Reroll Shards Earned\t41.28K",
                "Combat",
                "Damage dealt\t20.49aa",
                "Damage Taken\t81.77Q",
                "Damage Taken Wall\t466.01q",
                "Damage Taken While Berserked\t109.32Q",
                "Damage Gain From Berserk\tx8.00",
                "Death Defy\t22",
                "Lifesteal\t29.77T",
                "Projectiles Damage\t101.87D",
                "Projectiles Count\t16.36M",
                "Thorn damage\t3.29D",
                "Orb Damage\t15.66aa",
                "Enemies Hit by Orbs\t541.67K",
                "Land Mine Damage\t3.17O",
                "Land Mines Spawned\t191156",
                "Rend Armor Damage\t2.43N",
                "Death Ray Damage\t0",
                "Smart Missile Damage\t5.88O",
                "Inner Land Mine Damage\t44.53D",
                "Chain Lightning Damage\t240.24D",
                "Death Wave Damage\t10.65O",
                "Tagged by Deathwave\t282853",
                "Swamp Damage\t7.18D",
                "Black Hole Damage\t2.64aa",
                "Electrons Damage\t1.79aa",
                "Utility",
                "Waves Skipped\t2626",
                "Recovery Packages\t2138",
                "Free Attack Upgrade\t598",
                "Free Defense Upgrade\t992",
                "Free Utility Upgrade\t558",
                "HP From Death Wave\t0.00",
                "Coins From Death Wave\t436.98B",
                "Cash From Golden Tower\t$14.67B",
                "Coins From Golden Tower\t1.73q",
                "Coins From Black Hole\t3.10T",
                "Coins From Spotlight\t554.30B",
                "Coins From Orb\t0",
                "Coins from Coin Upgrade\t21.34T",
                "Coins from Coin Bonuses\t1.79q",
                "Enemies Destroyed",
                "Total Enemies\t618950",
                "Basic\t145774",
                "Fast\t149036",
                "Tank\t138135",
                "Ranged\t131640",
                "Boss\t476",
                "Protector\t692",
                "Total Elites\t5572",
                "Vampires\t1825",
                "Rays\t1935",
                "Scatters\t1812",
                "Saboteur\t0",
                "Commander\t2",
                "Overcharge\t3",
                "Destroyed By Orbs\t350039",
                "Destroyed by Thorns\t331",
                "Destroyed by Death Ray\t0",
                "Destroyed by Land Mine\t0",
                "Destroyed in Spotlight\t457932",
                "Bots",
                "Flame Bot Damage\t0",
                "Thunder Bot Stuns\t35.25K",
                "Golden Bot Coins Earned\t1.77T",
                "Destroyed in Golden Bot\t122295",
                "Guardian",
                "Damage\t0",
                "Summoned enemies\t47.49K",
                "Guardian coins stolen\t0",
                "Coins Fetched\t7.10T",
                "Gems\t0",
                "Medals\t0",
                "Reroll Shards\t240",
                "Cannon Shards\t0",
                "Armor Shards\t9",
                "Generator Shards\t9",
                "Core Shards\t3",
                "Common Modules\t1",
                "Rare Modules\t0",
                "",
            ]
        ),
        "\n".join(
            [
                "Battle Report",
                "Battle Date\tJan 02, 2026 05:53",
                "Game Time\t3d 3h 49m 30s",
                "Real Time\t15h 27m 7s",
                "Tier\t10",
                "Wave\t10899",
                "Killed By\tScatter",
                "Coins earned\t29.03T",
                "Coins per hour\t1.88T",
                "Cash earned\t$393.53B",
                "Interest earned\t$18.28M",
                "Gem Blocks Tapped\t10",
                "Cells Earned\t227.34K",
                "Reroll Shards Earned\t11.38K",
                "Combat",
                "Damage dealt\t730.58D",
                "Damage Taken\t9.99q",
                "Damage Taken Wall\t33.49q",
                "Damage Taken While Berserked\t0",
                "Damage Gain From Berserk\tx0.00",
                "Death Defy\t6",
                "Lifesteal\t528.61B",
                "Projectiles Damage\t3.22D",
                "Projectiles Count\t48.11M",
                "Thorn damage\t5.09D",
                "Orb Damage\t577.39D",
                "Enemies Hit by Orbs\t1.51M",
                "Land Mine Damage\t66.82s",
                "Land Mines Spawned\t568847",
                "Rend Armor Damage\t0",
                "Death Ray Damage\t0",
                "Smart Missile Damage\t448.87Q",
                "Inner Land Mine Damage\t0",
                "Chain Lightning Damage\t15.07O",
                "Death Wave Damage\t17.10Q",
                "Tagged by Deathwave\t526095",
                "Swamp Damage\t0",
                "Black Hole Damage\t67.98D",
                "Electrons Damage\t76.90D",
                "Utility",
                "Waves Skipped\t2191",
                "Recovery Packages\t5579",
                "Free Attack Upgrade\t470",
                "Free Defense Upgrade\t1188",
                "Free Utility Upgrade\t861",
                "HP From Death Wave\t0.00",
                "Coins From Death Wave\t62.69B",
                "Cash From Golden Tower\t$228.41B",
                "Coins From Golden Tower\t1.32T",
                "Coins From Black Hole\t576.26B",
                "Coins From Spotlight\t71.36B",
                "Coins From Orb\t0",
                "Coins from Coin Upgrade\t1.71T",
                "Coins from Coin Bonuses\t25.11T",
                "Enemies Destroyed",
                "Total Enemies\t1919987",
                "Basic\t675950",
                "Fast\t403095",
                "Tank\t378998",
                "Ranged\t347458",
                "Boss\t869",
                "Protector\t1640",
                "Total Elites\t11370",
                "Vampires\t3659",
                "Rays\t3874",
                "Scatters\t3837",
                "Saboteur\t0",
                "Commander\t0",
                "Overcharge\t0",
                "Destroyed By Orbs\t1510155",
                "Destroyed by Thorns\t90666",
                "Destroyed by Death Ray\t0",
                "Destroyed by Land Mine\t84171",
                "Destroyed in Spotlight\t697579",
                "Bots",
                "Flame Bot Damage\t0",
                "Thunder Bot Stuns\t0",
                "Golden Bot Coins Earned\t76.12B",
                "Destroyed in Golden Bot\t189557",
                "Guardian",
                "Damage\t0",
                "Summoned enemies\t85.95K",
                "Guardian coins stolen\t0",
                "Coins Fetched\t51.29B",
                "Gems\t20",
                "Medals\t10",
                "Reroll Shards\t432",
                "Cannon Shards\t36",
                "Armor Shards\t15",
                "Generator Shards\t36",
                "Core Shards\t33",
                "Common Modules\t7",
                "Rare Modules\t0",
                "",
            ]
        ),
    )

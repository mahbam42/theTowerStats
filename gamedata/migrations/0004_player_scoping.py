"""Bind GameData rows to Player ownership for multi-player isolation."""

from __future__ import annotations

from django.db import migrations, models
import django.db.models.deletion


def forwards(apps, schema_editor) -> None:
    """Populate new `player` foreign keys for existing single-player rows."""

    Player = apps.get_model("player_state", "Player")
    BattleReport = apps.get_model("gamedata", "BattleReport")
    BattleReportProgress = apps.get_model("gamedata", "BattleReportProgress")
    RunBot = apps.get_model("gamedata", "RunBot")
    RunGuardian = apps.get_model("gamedata", "RunGuardian")
    RunCombatUltimateWeapon = apps.get_model("gamedata", "RunCombatUltimateWeapon")
    RunUtilityUltimateWeapon = apps.get_model("gamedata", "RunUtilityUltimateWeapon")

    player = Player.objects.filter(user__username="mahbam42").first() or Player.objects.order_by("id").first()
    if player is None:
        return

    BattleReport.objects.filter(player__isnull=True).update(player=player)

    progresses = list(
        BattleReportProgress.objects.filter(player__isnull=True).select_related("battle_report")
    )
    for row in progresses:
        row.player_id = row.battle_report.player_id
    if progresses:
        BattleReportProgress.objects.bulk_update(progresses, ["player"])

    bots = list(RunBot.objects.filter(player__isnull=True).select_related("battle_report"))
    for row in bots:
        row.player_id = row.battle_report.player_id
    if bots:
        RunBot.objects.bulk_update(bots, ["player"])

    guardians = list(RunGuardian.objects.filter(player__isnull=True).select_related("battle_report"))
    for row in guardians:
        row.player_id = row.battle_report.player_id
    if guardians:
        RunGuardian.objects.bulk_update(guardians, ["player"])

    combat_uws = list(
        RunCombatUltimateWeapon.objects.filter(player__isnull=True).select_related("battle_report")
    )
    for row in combat_uws:
        row.player_id = row.battle_report.player_id
    if combat_uws:
        RunCombatUltimateWeapon.objects.bulk_update(combat_uws, ["player"])

    utility_uws = list(
        RunUtilityUltimateWeapon.objects.filter(player__isnull=True).select_related("battle_report")
    )
    for row in utility_uws:
        row.player_id = row.battle_report.player_id
    if utility_uws:
        RunUtilityUltimateWeapon.objects.bulk_update(utility_uws, ["player"])


def backwards(apps, schema_editor) -> None:
    """Null out the player foreign keys (dev convenience)."""

    BattleReport = apps.get_model("gamedata", "BattleReport")
    BattleReportProgress = apps.get_model("gamedata", "BattleReportProgress")
    RunBot = apps.get_model("gamedata", "RunBot")
    RunGuardian = apps.get_model("gamedata", "RunGuardian")
    RunCombatUltimateWeapon = apps.get_model("gamedata", "RunCombatUltimateWeapon")
    RunUtilityUltimateWeapon = apps.get_model("gamedata", "RunUtilityUltimateWeapon")

    BattleReport.objects.update(player=None)
    BattleReportProgress.objects.update(player=None)
    RunBot.objects.update(player=None)
    RunGuardian.objects.update(player=None)
    RunCombatUltimateWeapon.objects.update(player=None)
    RunUtilityUltimateWeapon.objects.update(player=None)


class Migration(migrations.Migration):
    dependencies = [
        ("player_state", "0006_player_user_and_player_fks"),
        ("gamedata", "0003_preset_snapshot"),
    ]

    operations = [
        migrations.AddField(
            model_name="battlereport",
            name="player",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="battle_reports",
                to="player_state.player",
            ),
        ),
        migrations.AlterField(
            model_name="battlereport",
            name="checksum",
            field=models.CharField(db_index=True, max_length=64),
        ),
        migrations.AddField(
            model_name="battlereportprogress",
            name="player",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="battle_report_progress",
                to="player_state.player",
            ),
        ),
        migrations.AddField(
            model_name="runbot",
            name="player",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="run_bots",
                to="player_state.player",
            ),
        ),
        migrations.AddField(
            model_name="runguardian",
            name="player",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="run_guardians",
                to="player_state.player",
            ),
        ),
        migrations.AddField(
            model_name="runcombatultimateweapon",
            name="player",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="run_combat_uws",
                to="player_state.player",
            ),
        ),
        migrations.AddField(
            model_name="runutilityultimateweapon",
            name="player",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="run_utility_uws",
                to="player_state.player",
            ),
        ),
        migrations.RunPython(forwards, backwards),
        migrations.AlterField(
            model_name="battlereport",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="battle_reports",
                to="player_state.player",
            ),
        ),
        migrations.AlterField(
            model_name="battlereportprogress",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="battle_report_progress",
                to="player_state.player",
            ),
        ),
        migrations.AlterField(
            model_name="runbot",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="run_bots",
                to="player_state.player",
            ),
        ),
        migrations.AlterField(
            model_name="runguardian",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="run_guardians",
                to="player_state.player",
            ),
        ),
        migrations.AlterField(
            model_name="runcombatultimateweapon",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="run_combat_uws",
                to="player_state.player",
            ),
        ),
        migrations.AlterField(
            model_name="runutilityultimateweapon",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="run_utility_uws",
                to="player_state.player",
            ),
        ),
        migrations.AddConstraint(
            model_name="battlereport",
            constraint=models.UniqueConstraint(
                fields=("player", "checksum"),
                name="uniq_player_battle_report_checksum",
            ),
        ),
    ]

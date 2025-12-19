"""Introduce user-bound Player ownership and propagate Player FKs.

This is Phase 8 / Pillar 1: Multiple Player Support.

The migration:
- renames `Player.name` -> `Player.display_name`,
- adds `Player.user` (1:1 to the auth user),
- adds `player` FKs to player-owned join/parameter rows,
- migrates existing single-player data into a Player named "mahbam42".
"""

from __future__ import annotations

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.db import migrations, models
import django.db.models.deletion


def _auth_user_model(apps):
    app_label, model_name = settings.AUTH_USER_MODEL.split(".")
    return apps.get_model(app_label, model_name)


def forwards(apps, schema_editor) -> None:
    """Migrate existing single-player data into a user-bound Player."""

    Player = apps.get_model("player_state", "Player")
    PlayerCardPreset = apps.get_model("player_state", "PlayerCardPreset")
    PlayerBotParameter = apps.get_model("player_state", "PlayerBotParameter")
    PlayerUltimateWeaponParameter = apps.get_model("player_state", "PlayerUltimateWeaponParameter")
    PlayerGuardianChipParameter = apps.get_model("player_state", "PlayerGuardianChipParameter")
    Group = apps.get_model("auth", "Group")
    User = _auth_user_model(apps)

    player_group, _ = Group.objects.get_or_create(name="player")
    Group.objects.get_or_create(name="admin")

    user, created_user = User.objects.get_or_create(username="mahbam42")
    if created_user:
        user.password = make_password(None)
        user.save(update_fields=["password"])
    user.groups.add(player_group)

    existing_player = Player.objects.order_by("id").first()
    if existing_player is None:
        Player.objects.create(
            user=user,
            display_name="mahbam42",
            card_slots_unlocked=0,
        )
    else:
        existing_player.display_name = "mahbam42"
        existing_player.user_id = user.id
        existing_player.save(update_fields=["display_name", "user"])

    card_presets = list(
        PlayerCardPreset.objects.filter(player__isnull=True).select_related("player_card__player")
    )
    for link in card_presets:
        link.player_id = link.player_card.player_id
    if card_presets:
        PlayerCardPreset.objects.bulk_update(card_presets, ["player"])

    bot_params = list(
        PlayerBotParameter.objects.filter(player__isnull=True).select_related("player_bot__player")
    )
    for row in bot_params:
        row.player_id = row.player_bot.player_id
    if bot_params:
        PlayerBotParameter.objects.bulk_update(bot_params, ["player"])

    uw_params = list(
        PlayerUltimateWeaponParameter.objects.filter(player__isnull=True).select_related(
            "player_ultimate_weapon__player"
        )
    )
    for row in uw_params:
        row.player_id = row.player_ultimate_weapon.player_id
    if uw_params:
        PlayerUltimateWeaponParameter.objects.bulk_update(uw_params, ["player"])

    guardian_params = list(
        PlayerGuardianChipParameter.objects.filter(player__isnull=True).select_related(
            "player_guardian_chip__player"
        )
    )
    for row in guardian_params:
        row.player_id = row.player_guardian_chip.player_id
    if guardian_params:
        PlayerGuardianChipParameter.objects.bulk_update(guardian_params, ["player"])


def backwards(apps, schema_editor) -> None:
    """Detach the migrated Player from the migration user (dev convenience)."""

    Player = apps.get_model("player_state", "Player")
    User = _auth_user_model(apps)

    user = User.objects.filter(username="mahbam42").first()
    if user is None:
        return
    Player.objects.filter(user=user).update(user=None, display_name="default")


class Migration(migrations.Migration):
    dependencies = [
        ("player_state", "0005_parameter_effective_values"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RenameField(
            model_name="player",
            old_name="name",
            new_name="display_name",
        ),
        migrations.AlterField(
            model_name="player",
            name="display_name",
            field=models.CharField(max_length=64),
        ),
        migrations.AddField(
            model_name="player",
            name="user",
            field=models.OneToOneField(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="player",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="playercardpreset",
            name="player",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="card_preset_links",
                to="player_state.player",
            ),
        ),
        migrations.AddField(
            model_name="playerbotparameter",
            name="player",
            field=models.ForeignKey(
                null=True,
                blank=True,
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bot_parameters",
                to="player_state.player",
            ),
        ),
        migrations.AddField(
            model_name="playerultimateweaponparameter",
            name="player",
            field=models.ForeignKey(
                null=True,
                blank=True,
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ultimate_weapon_parameters",
                to="player_state.player",
            ),
        ),
        migrations.AddField(
            model_name="playerguardianchipparameter",
            name="player",
            field=models.ForeignKey(
                null=True,
                blank=True,
                editable=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="guardian_chip_parameters",
                to="player_state.player",
            ),
        ),
        migrations.RunPython(forwards, backwards),
        migrations.AlterField(
            model_name="player",
            name="user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="player",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="playercardpreset",
            name="player",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="card_preset_links",
                to="player_state.player",
            ),
        ),
        migrations.AlterField(
            model_name="playerbotparameter",
            name="player",
            field=models.ForeignKey(
                editable=False,
                null=False,
                blank=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="bot_parameters",
                to="player_state.player",
            ),
        ),
        migrations.AlterField(
            model_name="playerultimateweaponparameter",
            name="player",
            field=models.ForeignKey(
                editable=False,
                null=False,
                blank=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="ultimate_weapon_parameters",
                to="player_state.player",
            ),
        ),
        migrations.AlterField(
            model_name="playerguardianchipparameter",
            name="player",
            field=models.ForeignKey(
                editable=False,
                null=False,
                blank=False,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="guardian_chip_parameters",
                to="player_state.player",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="playercardpreset",
            name="uniq_player_card_preset",
        ),
        migrations.AddConstraint(
            model_name="playercardpreset",
            constraint=models.UniqueConstraint(
                fields=("player", "player_card", "preset"),
                name="uniq_player_card_preset",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="playerbotparameter",
            name="uniq_player_bot_param",
        ),
        migrations.AddConstraint(
            model_name="playerbotparameter",
            constraint=models.UniqueConstraint(
                fields=("player", "player_bot", "parameter_definition"),
                name="uniq_player_bot_param",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="playerultimateweaponparameter",
            name="uniq_player_uw_param",
        ),
        migrations.AddConstraint(
            model_name="playerultimateweaponparameter",
            constraint=models.UniqueConstraint(
                fields=("player", "player_ultimate_weapon", "parameter_definition"),
                name="uniq_player_uw_param",
            ),
        ),
        migrations.RemoveConstraint(
            model_name="playerguardianchipparameter",
            name="uniq_player_guardian_param",
        ),
        migrations.AddConstraint(
            model_name="playerguardianchipparameter",
            constraint=models.UniqueConstraint(
                fields=("player", "player_guardian_chip", "parameter_definition"),
                name="uniq_player_guardian_param",
            ),
        ),
    ]

"""Phase 8 Pillar 1 validation helpers.

This module implements the hard precondition gate for Phase 8 Pillar 2.
It validates the Phase 8 Pillar 1 checklist (multiple player support) using a
mix of programmatic checks (Django model introspection) and lightweight code
inspection (source assertions for scoping patterns).
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import asdict
from pathlib import Path
import inspect
from typing import Any
from collections.abc import Callable

import yaml
from django.apps import apps


@dataclass(frozen=True, slots=True)
class ChecklistResult:
    """Result for a single checklist entry.

    Attributes:
        key: Stable checklist key (dot-separated path).
        status: Either "complete" or "failed".
        details: Short failure detail string when failed, otherwise empty.
    """

    key: str
    status: str
    details: str = ""


def validate_phase8_pillar1_checklist(*, checklist_path: str = "archive/prompt29.yml") -> dict[str, Any]:
    """Validate the Phase 8 Pillar 1 checklist and return a structured report.

    Args:
        checklist_path: Workspace-relative path to the YAML checklist.

    Returns:
        A dictionary with:
        - `checklist_path`
        - `items`: list[ChecklistResult]-like dicts
        - `all_complete`: bool
    """

    raw = Path(checklist_path).read_text(encoding="utf-8")
    payload = yaml.safe_load(raw) or {}

    checks: dict[str, tuple[str, Callable[[], None]]] = {
        "core_principles.analysis_engine_player_scoped": (
            "Analysis engine does not import Django models.",
            _check_analysis_engine_has_no_django_imports,
        ),
        "models.player_model_exists": ("Player model exists and is 1:1 with user.", _check_player_model),
        "models.player_fk_added_to_all_mutable_models": ("Owned models have Player FK.", _check_player_fk_on_owned_models),
        "models.global_reference_models_have_no_player_fk": (
            "Definitions remain global (no Player FK).",
            _check_definitions_have_no_player_fk,
        ),
        "authorization.groups_defined": ("Groups exist (admin/player).", _check_groups_exist),
        "queryset_enforcement.admin_queryset_filtered": ("Admin querysets are player-scoped.", _check_admin_queryset_scoped),
        "queryset_enforcement.list_views_filtered": ("Core list views derive Player from request.user.", _check_views_player_scoped),
        "admin_lockdown.save_model_sets_player_automatically": ("Admin save assigns ownership.", _check_admin_save_model_assigns_player),
        "api_safety.player_id_never_accepted_from_client": ("No client-controlled player id inputs.", _check_no_client_player_id_inputs),
        "onboarding.player_auto_created_on_user_creation": ("Player is auto-created for new users.", _check_player_auto_created),
        "validation.two_users_data_isolated": ("Regression test covers isolation.", _check_isolation_test_exists),
    }

    results: list[ChecklistResult] = []
    for key, (_label, check) in checks.items():
        try:
            check()
        except Exception as exc:  # noqa: BLE001 - this is a validator report
            results.append(ChecklistResult(key=key, status="failed", details=str(exc)))
        else:
            results.append(ChecklistResult(key=key, status="complete"))

    all_complete = all(r.status == "complete" for r in results)
    expected_final = bool(((payload.get("final_status") or {}).get("pillar_1_complete")))

    return {
        "checklist_path": checklist_path,
        "items": [asdict(r) for r in results],
        "all_complete": all_complete,
        "final_status_pillar_1_complete": expected_final,
    }


def _check_analysis_engine_has_no_django_imports() -> None:
    """Ensure analysis/ is free of direct Django imports."""

    analysis_dir = Path("analysis")
    for path in analysis_dir.rglob("*.py"):
        source = path.read_text(encoding="utf-8")
        if "import django" in source or "from django" in source:
            raise AssertionError(f"Found Django import in analysis module: {path}")


def _check_player_model() -> None:
    """Ensure Player model exists and is a 1:1 user extension."""

    Player = apps.get_model("player_state", "Player")
    user_field = Player._meta.get_field("user")
    if user_field.many_to_one or user_field.one_to_many or user_field.many_to_many:
        raise AssertionError("Player.user is not a OneToOne field.")
    if getattr(user_field.remote_field, "related_name", None) != "player":
        raise AssertionError("Player.user does not expose related_name='player'.")


def _check_player_fk_on_owned_models() -> None:
    """Ensure all player-scoped models contain a Player foreign key."""

    owned_models = [
        apps.get_model("gamedata", "BattleReport"),
        apps.get_model("gamedata", "BattleReportProgress"),
        apps.get_model("gamedata", "RunBot"),
        apps.get_model("gamedata", "RunGuardian"),
        apps.get_model("gamedata", "RunCombatUltimateWeapon"),
        apps.get_model("gamedata", "RunUtilityUltimateWeapon"),
        apps.get_model("player_state", "Preset"),
        apps.get_model("player_state", "ChartSnapshot"),
        apps.get_model("player_state", "PlayerCard"),
        apps.get_model("player_state", "PlayerBot"),
        apps.get_model("player_state", "PlayerBotParameter"),
        apps.get_model("player_state", "PlayerGuardianChip"),
        apps.get_model("player_state", "PlayerGuardianChipParameter"),
        apps.get_model("player_state", "PlayerUltimateWeapon"),
        apps.get_model("player_state", "PlayerUltimateWeaponParameter"),
    ]

    Player = apps.get_model("player_state", "Player")
    for model in owned_models:
        field = model._meta.get_field("player")
        if field.remote_field.model is not Player:
            raise AssertionError(f"{model.__name__}.player does not reference Player.")


def _check_definitions_have_no_player_fk() -> None:
    """Ensure global definition models do not include a player FK."""

    for model in apps.get_app_config("definitions").get_models():
        field_names = {f.name for f in model._meta.get_fields()}
        if "player" in field_names:
            raise AssertionError(f"Definitions model {model.__name__} unexpectedly has a player field.")


def _check_groups_exist() -> None:
    """Ensure the expected auth groups exist."""

    Group = apps.get_model("auth", "Group")
    missing = []
    for name in ("admin", "player"):
        if not Group.objects.filter(name=name).exists():
            missing.append(name)
    if missing:
        raise AssertionError(f"Missing groups: {', '.join(missing)}")


def _check_admin_queryset_scoped() -> None:
    """Ensure admin querysets include player scoping logic for non-superusers."""

    import gamedata.admin as gamedata_admin
    import player_state.admin as player_state_admin

    for module, cls_name in ((gamedata_admin, "PlayerScopedAdmin"), (player_state_admin, "PlayerScopedAdmin")):
        cls = getattr(module, cls_name)
        source = inspect.getsource(cls.get_queryset)
        if "__user" not in source:
            raise AssertionError(f"{module.__name__}.{cls_name}.get_queryset is missing player__user scoping.")
        if "is_superuser" not in source:
            raise AssertionError(f"{module.__name__}.{cls_name}.get_queryset is missing superuser bypass.")


def _check_admin_save_model_assigns_player() -> None:
    """Ensure admin save_model assigns ownership from request.user."""

    import gamedata.admin as gamedata_admin
    import player_state.admin as player_state_admin

    for module, cls_name in ((gamedata_admin, "PlayerScopedAdmin"), (player_state_admin, "PlayerScopedAdmin")):
        cls = getattr(module, cls_name)
        source = inspect.getsource(cls.save_model)
        if "request.user.player" not in source:
            raise AssertionError(f"{module.__name__}.{cls_name}.save_model does not assign request.user.player.")


def _check_views_player_scoped() -> None:
    """Ensure core views derive Player from request.user rather than accepting ids."""

    import core.views as core_views

    source = inspect.getsource(core_views._request_player)
    if "request.user.player" not in source and "user=request.user" not in source:
        raise AssertionError("core.views._request_player does not derive the player from request.user.")
    if "player_id" in source:
        raise AssertionError("core.views._request_player unexpectedly references player_id.")


def _check_no_client_player_id_inputs() -> None:
    """Ensure request handlers do not accept player ids from client payloads."""

    needles = (
        'get("player_id")',
        "get('player_id')",
        'name="player_id"',
        "name='player_id'",
    )
    for path in (Path("core/forms.py"), Path("core/views.py"), Path("player_state/forms.py")):
        if not path.exists():
            continue
        source = path.read_text(encoding="utf-8")
        if any(needle in source for needle in needles):
            raise AssertionError(f"Found client-controlled player identifiers in {path}.")


def _check_player_auto_created() -> None:
    """Ensure a post_save signal creates Player for new users."""

    source = Path("player_state/signals.py").read_text(encoding="utf-8")
    if "post_save" not in source or "Player" not in source:
        raise AssertionError("player_state.signals does not appear to create Player instances on user creation.")


def _check_isolation_test_exists() -> None:
    """Ensure a regression test exists for multi-player isolation."""

    test_path = Path("tests/test_multiplayer_isolation.py")
    content = test_path.read_text(encoding="utf-8")
    if "test_dashboard_and_battle_history_are_player_scoped" not in content:
        raise AssertionError("Isolation regression test is missing or renamed.")

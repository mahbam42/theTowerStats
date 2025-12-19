"""URL configuration for core views."""

from __future__ import annotations

from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("charts/", views.dashboard, name="charts"),
    path("charts/export-derived.csv", views.export_derived_metrics_csv, name="export_derived_metrics_csv"),
    path("demo/enable/", views.enable_demo_mode, name="enable_demo_mode"),
    path("demo/disable/", views.disable_demo_mode, name="disable_demo_mode"),
    path("battle-history/", views.battle_history, name="battle_history"),
    path("cards/", views.cards, name="cards"),
    path("ultimate-weapons/", views.ultimate_weapon_progress, name="ultimate_weapon_progress"),
    path("guardians/", views.guardian_progress, name="guardian_progress"),
    path("bots/", views.bots_progress, name="bots_progress"),
]

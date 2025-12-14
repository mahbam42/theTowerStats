"""URL configuration for core views."""

from __future__ import annotations

from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
]


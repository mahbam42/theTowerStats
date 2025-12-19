"""URL configuration for theTowerStats."""

from __future__ import annotations

from django.contrib import admin
from django.urls import include, path

from core import views as core_views

urlpatterns = [
    path("", include("core.urls")),
    path("accounts/login/", core_views.login_view, name="login"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("admin/", admin.site.urls),
]

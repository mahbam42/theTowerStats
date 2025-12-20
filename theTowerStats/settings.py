"""Django settings for theTowerStats.

This module supports both local development and production deployment.
Production configuration is driven by environment variables so secrets are not
checked into the repository.
"""

from __future__ import annotations

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

def _env_bool(name: str, *, default: bool) -> bool:
    """Parse a boolean environment variable.

    Args:
        name: Environment variable name.
        default: Value when the variable is not set.

    Returns:
        Parsed boolean value.
    """

    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "t", "yes", "y", "on"}


def _env_int(name: str, *, default: int) -> int:
    """Parse an integer environment variable.

    Args:
        name: Environment variable name.
        default: Value when the variable is not set.

    Returns:
        Parsed integer value.
    """

    raw = os.getenv(name)
    if raw is None:
        return default
    return int(raw.strip())


def _env_csv(name: str, *, default: list[str]) -> list[str]:
    """Parse a comma-separated environment variable into a list of strings.

    Args:
        name: Environment variable name.
        default: Value when the variable is not set.

    Returns:
        A list of non-empty, trimmed values.
    """

    raw = os.getenv(name)
    if raw is None:
        return default
    return [part.strip() for part in raw.split(",") if part.strip()]

DEBUG = _env_bool("DJANGO_DEBUG", default=True)

_DEV_SECRET_KEY = "dev-only-insecure-secret-key"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or (_DEV_SECRET_KEY if DEBUG else "")
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY is required when DJANGO_DEBUG is False.")

ALLOWED_HOSTS: list[str] = _env_csv(
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "[::1]"],
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "definitions.apps.DefinitionsConfig",
    "player_state.apps.PlayerStateConfig",
    "gamedata.apps.GameDataConfig",
    "core.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
if not DEBUG:
    MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "theTowerStats.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.demo_mode",
            ],
        },
    }
]

WSGI_APPLICATION = "theTowerStats.wsgi.application"

DATABASES = {
    "default": dj_database_url.config(
        default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        conn_max_age=_env_int("DJANGO_DB_CONN_MAX_AGE", default=60 if not DEBUG else 0),
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
if not DEBUG:
    STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

CSRF_TRUSTED_ORIGINS = _env_csv("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

SECURE_SSL_REDIRECT = _env_bool("DJANGO_SECURE_SSL_REDIRECT", default=not DEBUG)
SESSION_COOKIE_SECURE = _env_bool("DJANGO_SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = _env_bool("DJANGO_CSRF_COOKIE_SECURE", default=not DEBUG)

SECURE_HSTS_SECONDS = _env_int("DJANGO_SECURE_HSTS_SECONDS", default=3600 if not DEBUG else 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool(
    "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
    default=not DEBUG,
)
SECURE_HSTS_PRELOAD = _env_bool("DJANGO_SECURE_HSTS_PRELOAD", default=not DEBUG)

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = _env_bool("DJANGO_USE_X_FORWARDED_HOST", default=not DEBUG)
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "same-origin"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

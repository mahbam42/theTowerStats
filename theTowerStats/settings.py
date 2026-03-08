"""Django settings for theTowerStats.

This module supports both local development and production deployment.
Production configuration is driven by environment variables so secrets are not
checked into the repository.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from urllib.parse import urlparse

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file(path: Path) -> None:
    """Load environment variables from a simple ``.env`` file.

    Args:
        path: Filesystem path to the environment file.

    Returns:
        None. Missing files are ignored and existing environment variables win.
    """

    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        key, sep, value = line.partition("=")
        if not sep:
            continue
        key = key.strip()
        value = value.strip()
        if value and value[0] in {"\"", "'"} and value[-1] == value[0]:
            value = value[1:-1]
        os.environ.setdefault(key, value)


_load_env_file(BASE_DIR / ".env")


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

def _parse_hostname(value: str) -> str | None:
    """Parse a hostname from a raw hostname or URL string.

    Args:
        value: Hostname or URL-like value (may include scheme and path).

    Returns:
        Parsed hostname when present, otherwise None.
    """

    raw = value.strip()
    if not raw:
        return None

    parsed = urlparse(raw if "://" in raw else f"http://{raw}")
    return parsed.hostname


def _is_running_tests() -> bool:
    """Return True when settings are loaded under a test runner.

    Args:
        None.

    Returns:
        True when pytest or Django's test runner appears to be active.
    """

    return (
        "pytest" in sys.modules
        or any(arg in {"test", "pytest"} for arg in sys.argv)
    )


def _env_platform_hosts(names: list[str]) -> list[str]:
    """Collect hostnames from platform-provided environment variables.

    This is primarily intended for hosted platforms (such as Railway) that
    provide a public URL or domain via environment variables.

    Args:
        names: Environment variable names to check for hostnames or URLs.

    Returns:
        A list of hostnames extracted from the provided environment variables.
    """

    hosts: list[str] = []
    for name in names:
        raw = os.getenv(name)
        if not raw:
            continue
        for part in raw.split(","):
            hostname = _parse_hostname(part)
            if hostname and hostname not in hosts:
                hosts.append(hostname)
    return hosts

DEBUG = _env_bool("DJANGO_DEBUG", default=True)
RUNNING_TESTS = _is_running_tests()

_DEV_SECRET_KEY = "dev-only-insecure-secret-key"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or (_DEV_SECRET_KEY if DEBUG else "")
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY is required when DJANGO_DEBUG is False.")

_DJANGO_ALLOWED_HOSTS_RAW = os.getenv("DJANGO_ALLOWED_HOSTS")
ALLOWED_HOSTS: list[str] = _env_csv(
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "[::1]"],
)

_PLATFORM_HOSTS = _env_platform_hosts(
    [
        "RAILWAY_PUBLIC_DOMAIN",
        "RAILWAY_PUBLIC_URL",
        "RAILWAY_STATIC_URL",
        "RAILWAY_URL",
    ]
)
for _platform_host in _PLATFORM_HOSTS:
    if _platform_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_platform_host)

if not DEBUG and _DJANGO_ALLOWED_HOSTS_RAW is None and not _PLATFORM_HOSTS:
    raise RuntimeError(
        "DJANGO_ALLOWED_HOSTS is required in production. "
        "Set DJANGO_ALLOWED_HOSTS or provide a platform domain via "
        "RAILWAY_PUBLIC_DOMAIN/RAILWAY_PUBLIC_URL/RAILWAY_STATIC_URL."
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
                "core.context_processors.motd_banner",
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
if RUNNING_TESTS:
    _DJANGO_TEST_DATABASE_URL = os.getenv("DJANGO_TEST_DATABASE_URL")
    _DJANGO_TEST_USE_SQLITE = _env_bool(
        "DJANGO_TEST_USE_SQLITE",
        default=os.getenv("GITHUB_ACTIONS") is None,
    )
    if _DJANGO_TEST_DATABASE_URL:
        DATABASES["default"] = dj_database_url.parse(
            _DJANGO_TEST_DATABASE_URL,
            conn_max_age=_env_int("DJANGO_DB_CONN_MAX_AGE", default=0),
        )
    elif _DJANGO_TEST_USE_SQLITE:
        DATABASES["default"] = dj_database_url.parse(
            f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
            conn_max_age=_env_int("DJANGO_DB_CONN_MAX_AGE", default=0),
        )

_DB_CONNECT_TIMEOUT = _env_int("DJANGO_DB_CONNECT_TIMEOUT", default=5)
_DB_STATEMENT_TIMEOUT_MS = _env_int("DJANGO_DB_STATEMENT_TIMEOUT_MS", default=0)
_default_database = DATABASES["default"]
if str(_default_database.get("ENGINE", "")).startswith("django.db.backends.postgresql"):
    _db_options = _default_database.setdefault("OPTIONS", {})
    if _DB_CONNECT_TIMEOUT > 0:
        _db_options.setdefault("connect_timeout", _DB_CONNECT_TIMEOUT)
    if _DB_STATEMENT_TIMEOUT_MS > 0:
        _existing_options = str(_db_options.get("options", "")).strip()
        _timeout_flag = f"-c statement_timeout={_DB_STATEMENT_TIMEOUT_MS}"
        if _timeout_flag not in _existing_options.split():
            _db_options["options"] = f"{_existing_options} {_timeout_flag}".strip()

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"

CHANGELOG_GITHUB_URL = "https://github.com/mahbam42/theTowerStats/blob/main/CHANGELOG.md"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
if not DEBUG and not RUNNING_TESTS:
    STORAGES["staticfiles"]["BACKEND"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

_DJANGO_CSRF_TRUSTED_ORIGINS_RAW = os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS")
CSRF_TRUSTED_ORIGINS = _env_csv("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])
if not DEBUG and _DJANGO_CSRF_TRUSTED_ORIGINS_RAW is None and _PLATFORM_HOSTS:
    for _platform_host in _PLATFORM_HOSTS:
        origin = f"https://{_platform_host}"
        if origin not in CSRF_TRUSTED_ORIGINS:
            CSRF_TRUSTED_ORIGINS.append(origin)

SECURE_SSL_REDIRECT = _env_bool("DJANGO_SECURE_SSL_REDIRECT", default=not DEBUG)
SESSION_COOKIE_SECURE = _env_bool("DJANGO_SESSION_COOKIE_SECURE", default=not DEBUG)
CSRF_COOKIE_SECURE = _env_bool("DJANGO_CSRF_COOKIE_SECURE", default=not DEBUG)
if RUNNING_TESTS:
    SECURE_SSL_REDIRECT = False

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

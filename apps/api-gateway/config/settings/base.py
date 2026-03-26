from __future__ import annotations

import os
import sys
from pathlib import Path

from infrastructure.observability.logging import build_logging_config


BASE_DIR = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = BASE_DIR.parents[1] if len(BASE_DIR.parents) > 1 else Path("/workspace")


def resolve_auth_lib_dir() -> Path:
    candidates = [WORKSPACE_ROOT / "libs" / "auth" / "src", Path("/workspace/libs/auth/src")]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


AUTH_LIB_DIR = resolve_auth_lib_dir()

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

if str(AUTH_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(AUTH_LIB_DIR))


def load_env_file(env_path: Path) -> None:
    if not env_path.exists():
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env_file(BASE_DIR / ".env.example")
load_env_file(BASE_DIR / ".env")

APP_ENV = os.getenv("APP_ENV", "local")
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "api-gateway-dev-secret")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "*").split(",") if host.strip()]
PORT = int(os.getenv("PORT", "8000"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
APPEND_SLASH = False

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "strawberry.django",
    "apps.rest_api",
    "apps.graphql_api",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "infrastructure.auth.middleware.OptionalJWTAuthenticationMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

USE_POSTGRES = os.getenv("API_GATEWAY_USE_POSTGRES", "false").lower() == "true"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.dummy",
    }
}

if USE_POSTGRES:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "api_gateway"),
            "USER": os.getenv("POSTGRES_USER", "api_gateway"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "api_gateway"),
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
        }
    }

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "EXCEPTION_HANDLER": "apps.rest_api.exceptions.api_exception_handler",
    "UNAUTHENTICATED_USER": None,
}

JWT_ISSUER = os.getenv("JWT_ISSUER", "https://identity.aerolytic.local")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "aerolytic-clients")
IDENTITY_SERVICE_BASE_URL = os.getenv(
    "IDENTITY_SERVICE_BASE_URL",
    os.getenv("IDENTITY_SERVICE_URL", "http://127.0.0.1:8001"),
)
CRM_SERVICE_BASE_URL = os.getenv("CRM_SERVICE_BASE_URL", "http://127.0.0.1:8002")
WORKFLOW_SERVICE_BASE_URL = os.getenv("WORKFLOW_SERVICE_BASE_URL", "http://127.0.0.1:8003")
JWT_JWKS_URL = os.getenv(
    "JWT_JWKS_URL",
    os.getenv("JWKS_URL", f"{IDENTITY_SERVICE_BASE_URL}/api/v1/auth/jwks/"),
)
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        "http://localhost:4200,http://127.0.0.1:4200,http://localhost:4300,http://127.0.0.1:4300",
    ).split(",")
    if origin.strip()
]
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-requested-with",
    "x-csrftoken",
]
CORS_ALLOW_METHODS = ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"]
CORS_ALLOW_CREDENTIALS = True
CORS_URLS_REGEX = r"^/(api/.*|graphql)$"
CSRF_TRUSTED_ORIGINS = CORS_ALLOWED_ORIGINS

LOGGING = build_logging_config(LOG_LEVEL)
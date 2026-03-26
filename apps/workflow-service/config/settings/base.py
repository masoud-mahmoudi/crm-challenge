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
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "workflow-service-dev-secret")
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
ALLOWED_HOSTS = [host.strip() for host in os.getenv("ALLOWED_HOSTS", "*").split(",") if host.strip()]
PORT = int(os.getenv("PORT", "8003"))
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DB_SCHEMA = os.getenv("DB_SCHEMA", "workflow")
REQUEST_TIMEOUT_SECONDS = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "10"))
WORKFLOW_MAX_RETRIES = int(os.getenv("WORKFLOW_MAX_RETRIES", "3"))

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
APPEND_SLASH = True

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "apps.workflows",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "infrastructure.auth.middleware.OptionalJWTAuthenticationMiddleware",
]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB", os.getenv("DB_NAME", "crm_aerialytic")),
        "USER": os.getenv("POSTGRES_USER", os.getenv("DB_USER", "app_db_user")),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD", os.getenv("DB_PASSWORD", "app_db_password")),
        "HOST": os.getenv("POSTGRES_HOST", os.getenv("DB_HOST", "localhost")),
        "PORT": os.getenv("POSTGRES_PORT", os.getenv("DB_PORT", "5432")),
        "OPTIONS": {"options": f"-c search_path={DB_SCHEMA}"},
        "TEST": {
            "NAME": os.getenv(
                "DB_TEST_NAME",
                f"test_{os.getenv('POSTGRES_DB', os.getenv('DB_NAME', 'crm_aerialytic'))}",
            )
        },
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
    "EXCEPTION_HANDLER": "apps.workflows.exceptions.api_exception_handler",
    "UNAUTHENTICATED_USER": None,
}

JWT_ISSUER = os.getenv("JWT_ISSUER", "https://identity.aerolytic.local")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "aerolytic-clients")
JWT_JWKS_URL = os.getenv("JWT_JWKS_URL", "http://127.0.0.1:8001/api/v1/auth/jwks/")
CRM_SERVICE_BASE_URL = os.getenv("CRM_SERVICE_BASE_URL", "http://127.0.0.1:8002")
IDENTITY_SERVICE_BASE_URL = os.getenv("IDENTITY_SERVICE_BASE_URL", "http://127.0.0.1:8001")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:29092")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "workflow-service")
INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN", "")

LOGGING = build_logging_config(LOG_LEVEL)

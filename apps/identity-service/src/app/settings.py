import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_ROOT = BASE_DIR.parents[2]
AUTH_LIB_DIR = WORKSPACE_ROOT / "libs" / "auth" / "src"

if str(AUTH_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(AUTH_LIB_DIR))

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "identity-service-dev-secret")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "app.urls"
WSGI_APPLICATION = "app.wsgi.application"

INSTALLED_APPS = []

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

DATABASES = {}

USE_TZ = True
TIME_ZONE = "UTC"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

JWT_ISSUER = os.getenv("JWT_ISSUER", "https://identity.aerolytic.local")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "aerolytic-clients")
ACCESS_TOKEN_TTL_SECONDS = int(os.getenv("ACCESS_TOKEN_TTL_SECONDS", "3600"))
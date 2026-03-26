from __future__ import annotations

from .base import *  # noqa: F403


DEBUG = False
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
LOGGING = {}
INTERNAL_SERVICE_TOKEN = "test-internal-token"

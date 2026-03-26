from __future__ import annotations

from .base import *  # noqa: F403


DEBUG = False
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.dummy",
    }
}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
LOGGING = {}
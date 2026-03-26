import os
from pathlib import Path

from .base import *  # noqa: F403


DEBUG = True

postgres_explicitly_configured = any(
	os.getenv(setting_name)
	for setting_name in ("POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST", "POSTGRES_PORT")
)

if not postgres_explicitly_configured and not os.getenv("IDENTITY_SERVICE_FORCE_POSTGRES"):
	DATABASES = {
		"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": Path(BASE_DIR) / "db.sqlite3"}  # noqa: F405
	}

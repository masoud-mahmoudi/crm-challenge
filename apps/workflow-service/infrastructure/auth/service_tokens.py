from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def get_internal_service_token() -> str:
    token = settings.INTERNAL_SERVICE_TOKEN
    if not token:
        raise ImproperlyConfigured("INTERNAL_SERVICE_TOKEN must be configured")
    return token

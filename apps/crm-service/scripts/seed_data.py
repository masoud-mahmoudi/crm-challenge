from __future__ import annotations

import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

import django


django.setup()

from apps.crm.models import Lead  # noqa: E402


def main() -> None:
    Lead.objects.get_or_create(
        company_id="11111111-1111-1111-1111-111111111111",
        created_by_user_id="33333333-3333-3333-3333-333333333333",
        name="Demo Lead Toronto",
        defaults={
            "email": "toronto@example.com",
            "source": "seed",
        },
    )
    Lead.objects.get_or_create(
        company_id="22222222-2222-2222-2222-222222222222",
        created_by_user_id="44444444-4444-4444-4444-444444444444",
        name="Demo Lead Montreal",
        defaults={
            "email": "montreal@example.com",
            "source": "seed",
        },
    )
    print("CRM seed data created.")


if __name__ == "__main__":
    main()
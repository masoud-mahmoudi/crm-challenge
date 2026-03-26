from __future__ import annotations

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Ensure the workflow PostgreSQL schema exists before migrations run"

    def handle(self, *args, **options):
        if connection.vendor != "postgresql":
            self.stdout.write("Skipping schema creation because the active database is not PostgreSQL.")
            return

        with connection.cursor() as cursor:
            cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{settings.DB_SCHEMA}"')
        self.stdout.write(self.style.SUCCESS(f'Ensured PostgreSQL schema "{settings.DB_SCHEMA}" exists.'))

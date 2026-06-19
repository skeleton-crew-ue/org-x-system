from datetime import date
from pathlib import Path
from urllib.parse import urlparse
import os
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Backup PostgreSQL database using pg_dump"

    def handle(self, *args, **options):
        db_engine = settings.DATABASES["default"]["ENGINE"]

        if "sqlite3" in db_engine:
            self.stdout.write(
                self.style.WARNING(
                    "SQLite detected. Skipping database backup."
                )
            )
            return

        database_url = os.environ.get("DATABASE_URL")

        if not database_url:
            self.stderr.write("DATABASE_URL is not configured.")
            return

        parsed = urlparse(database_url)

        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)

        filename = f"{date.today()}-orgx.sql"
        backup_file = backup_dir / filename

        env = os.environ.copy()
        env["PGPASSWORD"] = parsed.password or ""

        command = [
            "pg_dump",
            "-h",
            parsed.hostname,
            "-p",
            str(parsed.port or 5432),
            "-U",
            parsed.username,
            "-d",
            parsed.path.lstrip("/"),
            "-f",
            str(backup_file),
        ]

        try:
            subprocess.run(
                command,
                env=env,
                check=True,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Backup written to {backup_file}"
                )
            )
        except subprocess.CalledProcessError as exc:
            self.stderr.write(
                f"Backup failed: {exc}"
            )
from django.core.management.base import BaseCommand
from django.db import transaction
from members.models import User

import pandas as pd
import re
from dateutil import parser


EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class Command(BaseCommand):
    help = "Import members from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_path")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--skip-existing", action="store_true")

    def handle(self, *args, **options):
        path = options["csv_path"]
        dry_run = options["dry_run"]
        skip_existing = options["skip_existing"]

        df = pd.read_csv(path, dtype=str, keep_default_na=False)

        created = 0
        skipped = 0
        errors = 0

        self.stdout.write(f"Rows loaded: {len(df)}")

        for i, row in df.iterrows():

            email = row.get("email", "").strip().lower()
            member_id = row.get("member_id", "").strip()
            phone = row.get("phone", "").strip()
            name = row.get("name", "").strip()
            joined_at_raw = row.get("joined_at", "").strip()

            # EMAIL VALIDATION
            if not email or not re.match(EMAIL_REGEX, email):
                self.stdout.write(f"Skipping invalid email at row {i}")
                skipped += 1
                continue

            # SKIP EXISTING
            if skip_existing and User.objects.filter(email=email).exists():
                skipped += 1
                continue

            # PHONE CLEANING
            digits = re.sub(r"\D", "", phone)
            if len(digits) == 9:
                phone = "+995" + digits

            # JOIN DATE PARSING
            try:
                joined_at = parser.parse(joined_at_raw).date() if joined_at_raw else None
            except Exception:
                joined_at = None
                errors += 1

            # MEMBER ID FIX
            if not member_id:
                member_id = f"M-{100000 + i}"

            if dry_run:
                continue

            with transaction.atomic():
                User.objects.create(
                    username=email.split("@")[0] + str(i),
                    email=email,
                    member_id=member_id,
                    phone=phone,
                    joined_at=joined_at,
                    role=User.Role.MEMBER,
                )

                created += 1

        self.stdout.write(self.style.SUCCESS(
            f"""
IMPORT COMPLETE
Created: {created}
Skipped: {skipped}
Errors: {errors}
"""
        ))
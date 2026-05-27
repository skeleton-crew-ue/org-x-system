"""Custom user model for the Org X System.

This is the schema spine — every other module's `created_by` / `uploaded_by` /
`voter` foreign key points here. Defined as a thin stub in the bootstrap so the
custom user model exists from the very first migration.

Mr H owns fleshing this out (registration, profile flows, data migration).
Field definitions follow docs/Database_ERD.md §2.1.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"

    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.MEMBER
    )
    # Nullable so `createsuperuser` works (the superuser has no member_id).
    # The 4,000-row migration populates this for real members. (Postgres and
    # SQLite both allow multiple NULLs under a UNIQUE constraint.)
    member_id = models.CharField(
        max_length=20, unique=True, null=True, blank=True
    )
    phone = models.CharField(max_length=20, blank=True)
    joined_at = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

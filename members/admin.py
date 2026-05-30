"""Admin registration for the custom User.

Minimal bootstrap registration so the User is manageable in Django Admin from
day one. Mr H expands this into the full MemberAdmin (search, filters, bulk
actions) — see docs/Project_Plan_Org_X.md §4.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "role", "member_id", "is_staff")
    list_filter = BaseUserAdmin.list_filter + ("role",)
    # Add our custom fields to the default edit form.
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Org X", {"fields": ("role", "member_id", "phone", "joined_at")}),
    )

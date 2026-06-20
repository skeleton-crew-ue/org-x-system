from django.contrib import admin
from .models import Meeting

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("title", "scheduled_at", "status")
    list_filter = ("status",)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        
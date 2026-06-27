from django.contrib import admin
from .models import Broadcast


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display  = ("subject", "recipient_filter", "sent_by", "sent_at", "recipient_count")
    readonly_fields = ("sent_by", "sent_at", "recipient_count")

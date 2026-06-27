from django.contrib import admin

from .models import Broadcast, ChatAnalysis, ChatExport


@admin.register(ChatExport)
class ChatExportAdmin(admin.ModelAdmin):
    list_display = ("source_group_name", "uploaded_by", "uploaded_at", "message_count")
    search_fields = ("source_group_name",)
    list_filter = ("uploaded_at",)


@admin.register(ChatAnalysis)
class ChatAnalysisAdmin(admin.ModelAdmin):
    list_display = ("chat_export", "generated_at")
    list_filter = ("generated_at",)


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ("subject", "sent_by", "sent_at", "recipient_filter", "recipient_count")
    search_fields = ("subject",)
    list_filter = ("recipient_filter", "sent_at")

from django.contrib import admin

from .models import ChatAnalysis, ChatExport


@admin.register(ChatExport)
class ChatExportAdmin(admin.ModelAdmin):
    list_display = ("source_group_name", "uploaded_by", "uploaded_at", "message_count")
    search_fields = ("source_group_name",)
    list_filter = ("uploaded_at",)


@admin.register(ChatAnalysis)
class ChatAnalysisAdmin(admin.ModelAdmin):
    list_display = ("chat_export", "generated_at")
    list_filter = ("generated_at",)

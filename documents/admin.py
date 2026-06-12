from django.contrib import admin
from .models import Document, Tag

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_by", "uploaded_at")
    search_fields = ("title",)
    list_filter = ("uploaded_at", "tags")

from django.contrib import admin

from .models import Document, Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_by", "uploaded_at")
    list_filter = ("tags", "uploaded_at")
    search_fields = ("title", "description")
    filter_horizontal = ("tags",)
    readonly_fields = ("uploaded_at",)

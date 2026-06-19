from django.contrib import admin

from .models import Ballot, BallotOption, Vote


class BallotOptionInline(admin.TabularInline):
    model = BallotOption
    extra = 2


@admin.register(Ballot)
class BallotAdmin(admin.ModelAdmin):
    list_display = ("title", "opens_at", "closes_at", "is_active")
    list_filter = ("is_active",)
    inlines = [BallotOptionInline]
    readonly_fields = ("created_by",)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Vote)

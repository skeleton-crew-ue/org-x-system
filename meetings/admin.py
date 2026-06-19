from django.contrib import admin
from .models import Meeting

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'duration_minutes', 'created_by')
    list_filter = ('date', 'created_by')
    search_fields = ('title', 'minutes')
    
# Register your models here.

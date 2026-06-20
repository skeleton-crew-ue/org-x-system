from django.contrib import admin
from .models import Category, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "type")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("amount", "transaction_date", "type", "category", "recorded_by")
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)
        
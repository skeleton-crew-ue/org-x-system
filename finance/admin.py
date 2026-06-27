from django.contrib import admin
from .models import Category, Transaction

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')
    list_filter = ('type',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction_date', 'type', 'category', 'amount', 'recorded_by')
    list_filter = ('type', 'category', 'transaction_date')
    search_fields = ('description',)
    
# apps/inventory/admin.py
from django.contrib import admin
from .models import FoodicsData

@admin.register(FoodicsData)
class FoodicsDataAdmin(admin.ModelAdmin):
    list_display = ('sku', 'branch', 'stock_level', 'expiry_date', 'last_synced')
    list_filter = ('branch', 'expiry_date')
    search_fields = ('sku', 'batch_id')
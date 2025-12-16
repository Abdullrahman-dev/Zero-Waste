# apps/analytics/admin.py
from django.contrib import admin
from .models import WasteReport

@admin.register(WasteReport)
class WasteReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'branch', 'total_waste_value', 'generated_date')
    list_filter = ('branch', 'generated_date')
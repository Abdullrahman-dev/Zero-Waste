# apps/core/admin.py
from django.contrib import admin
from .models import RestaurantCompany, Branch

@admin.register(RestaurantCompany)
class RestaurantCompanyAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'subscription_status', 'created_at')
    search_fields = ('name',)

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'location')
    list_filter = ('company',)
    search_fields = ('name', 'location')
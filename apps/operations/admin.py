# apps/operations/admin.py
from django.contrib import admin
from .models import OperationalRequest, SupportTicket

@admin.register(OperationalRequest)
class OperationalRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'type', 'branch', 'status', 'submitted_by', 'created_at')
    list_filter = ('status', 'type')
    list_editable = ('status',) # يسمح بتغيير الحالة مباشرة من القائمة

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'priority', 'status', 'created_at')
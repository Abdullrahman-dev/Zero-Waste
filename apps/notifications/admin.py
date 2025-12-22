from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from .models import EmailLog, SystemUpdate, UserNotification


class NotificationAdminSite(admin.AdminSite):
    """تخصيص Admin Site لإضافة صفحة الإشعارات"""
    
    def get_urls(self):
        from .admin_views import notification_dashboard, send_notification_now
        
        urls = super().get_urls()
        custom_urls = [
            path('notifications/dashboard/', 
                 self.admin_view(notification_dashboard), 
                 name='notification_dashboard'),
            path('notifications/send/<int:update_id>/', 
                 self.admin_view(send_notification_now), 
                 name='send_notification_now'),
        ]
        return custom_urls + urls


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    """إدارة سجلات الإيميلات"""
    list_display = ['recipient', 'email_type', 'subject', 'is_sent', 'sent_at']
    list_filter = ['email_type', 'is_sent', 'sent_at']
    search_fields = ['recipient', 'subject', 'body']
    readonly_fields = ['sent_at']
    date_hierarchy = 'sent_at'
    
    def has_add_permission(self, request):
        """منع إضافة سجلات يدوياً"""
        return False


@admin.register(SystemUpdate)
class SystemUpdateAdmin(admin.ModelAdmin):
    """إدارة تحديثات النظام"""
    list_display = ['title', 'scheduled_time', 'is_sent', 'send_email', 'send_notification', 'created_at']
    list_filter = ['is_sent', 'send_email', 'send_notification', 'created_at']
    search_fields = ['title', 'message']
    readonly_fields = ['created_at', 'is_sent']
    date_hierarchy = 'scheduled_time'
    actions = ['send_update_notifications']
    
    fieldsets = (
        ('معلومات التحديث', {
            'fields': ('title', 'message', 'scheduled_time')
        }),
        ('خيارات الإرسال', {
            'fields': ('send_email', 'send_notification')
        }),
        ('معلومات النظام', {
            'fields': ('created_by', 'created_at', 'is_sent'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """حفظ المستخدم الذي أنشأ التحديث"""
        if not change:  # إذا كان جديد
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def send_update_notifications(self, request, queryset):
        """إرسال الإشعارات للمدراء"""
        from .utils import send_system_update_notification
        
        sent_count = 0
        for update in queryset.filter(is_sent=False):
            count = send_system_update_notification(update)
            sent_count += count
        
        self.message_user(
            request,
            f"تم إرسال الإشعارات بنجاح إلى {sent_count} مدير."
        )
    
    send_update_notifications.short_description = "إرسال الإشعارات للمدراء"


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    """إدارة الإشعارات الداخلية"""
    list_display = ['user', 'title', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        """السماح بإضافة إشعارات يدوياً"""
        return True

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'نظام الإشعارات والإيميلات'

    def ready(self):
        """استيراد الـ signals عند تشغيل التطبيق"""
        import apps.notifications.signals

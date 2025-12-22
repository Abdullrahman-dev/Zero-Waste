from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.authentication.models import User
from .utils import send_welcome_email, create_in_app_notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def send_welcome_email_on_registration(sender, instance, created, **kwargs):
    """
    إرسال إيميل ترحيب تلقائياً عند إنشاء حساب جديد
    للمدراء فقط (General Manager و Branch Manager)
    """
    if created and instance.role in ['manager', 'branch_manager']:
        # التحقق من وجود إيميل
        if instance.email:
            logger.info(f"New user created: {instance.username} ({instance.get_role_display()})")
            
            # إرسال إيميل الترحيب
            send_welcome_email(instance)
            
            # إنشاء إشعار داخلي ترحيبي
            create_in_app_notification(
                user=instance,
                title="مرحباً بك في نظام Zero Waste!",
                message=f"تم إنشاء حسابك بنجاح كـ {instance.get_role_display()}. يمكنك الآن البدء باستخدام النظام.",
                notification_type='welcome'
            )
        else:
            logger.warning(f"User {instance.username} created without email address")

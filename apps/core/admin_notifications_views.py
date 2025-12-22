from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from apps.notifications.models import SystemUpdate, UserNotification, EmailLog
from apps.notifications.utils import send_system_update_notification
from apps.authentication.models import User


@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='login')
def admin_notifications_dashboard(request):
    """
    صفحة إدارة الإشعارات للسوبر أدمن فقط
    """
    if request.method == 'POST':
        # إنشاء إشعار جديد
        title = request.POST.get('title')
        message = request.POST.get('message')
        scheduled_time = request.POST.get('scheduled_time')
        send_email = request.POST.get('send_email') == 'on'
        send_notification = request.POST.get('send_notification') == 'on'
        send_now = request.POST.get('send_now') == 'on'
        target_type = request.POST.get('target_type', 'managers')
        selected_users = request.POST.getlist('selected_users')
        
        if title and message and scheduled_time:
            update = SystemUpdate.objects.create(
                title=title,
                message=message,
                scheduled_time=scheduled_time,
                created_by=request.user,
                send_email=send_email,
                send_notification=send_notification,
                target_type=target_type
            )
            
            # إضافة المستخدمين المحددين إذا كان الاستهداف انتقائي
            if target_type == 'selected' and selected_users:
                update.target_users.set(selected_users)
            
            # إرسال فوراً إذا تم تحديد الخيار
            if send_now:
                count = send_system_update_notification(update)
                messages.success(request, f'✅ تم إرسال الإشعار بنجاح إلى {count} مستخدم')
            else:
                messages.success(request, '✅ تم حفظ الإشعار بنجاح. يمكنك إرساله لاحقاً.')
            
            return redirect('core:admin_notifications')
    
    # إحصائيات
    total_notifications = UserNotification.objects.count()
    unread_notifications = UserNotification.objects.filter(is_read=False).count()
    total_emails = EmailLog.objects.count()
    successful_emails = EmailLog.objects.filter(is_sent=True).count()
    pending_updates = SystemUpdate.objects.filter(is_sent=False).count()
    
    # آخر الإشعارات المرسلة
    recent_updates = SystemUpdate.objects.all().order_by('-created_at')[:10]
    
    # آخر الإيميلات
    recent_emails = EmailLog.objects.all().order_by('-sent_at')[:10]
    
    # جميع المستخدمين للاختيار
    all_users = User.objects.all().order_by('username')
    managers = User.objects.filter(role__in=['manager', 'branch_manager']).order_by('username')
    
    context = {
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'total_emails': total_emails,
        'successful_emails': successful_emails,
        'pending_updates': pending_updates,
        'recent_updates': recent_updates,
        'recent_emails': recent_emails,
        'all_users': all_users,
        'managers': managers,
        'total_users': User.objects.count(),
    }
    
    return render(request, 'core/admin_notifications.html', context)


@login_required
@user_passes_test(lambda u: u.is_superuser, login_url='login')
def send_notification_now(request, update_id):
    """إرسال إشعار محفوظ - للسوبر أدمن فقط"""
    if request.method == 'POST':
        try:
            update = SystemUpdate.objects.get(id=update_id)
            count = send_system_update_notification(update)
            messages.success(request, f'✅ تم إرسال الإشعار بنجاح إلى {count} مستخدم')
        except SystemUpdate.DoesNotExist:
            messages.error(request, '❌ الإشعار غير موجود')
    
    return redirect('core:admin_notifications')

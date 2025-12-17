# apps/operations/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404 , render , redirect
from django.contrib.auth import get_user_model
from apps.core.models import Branch
from .models import OperationalRequest
from apps.analytics.models import WasteReport
from django.db.models import Sum


User = get_user_model()

# 1. محاكاة: مدير الفرع يرسل طلب عرض خاص
def create_promo_request(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    
    # إنشاء الطلب في الداتابيس
    OperationalRequest.objects.create(
        branch=branch,
        type='PROMO_CAMPAIGN',
        details=f'طلب تلقائي بناءً على تقرير الذكاء الاصطناعي للفرع: {branch.name}',
        status='PENDING'
    )
    
    # بدلاً من json، نعيد توجيه المستخدم لصفحة العمليات ليرى الطلب
    return redirect('requests_list')

# 2. محاكاة: المدير العام يوافق على الطلب
def review_request(request, request_id, action):
    op_request = get_object_or_404(OperationalRequest, id=request_id)
    
    if action == 'approve':
        op_request.status = OperationalRequest.RequestStatus.APPROVED
        msg = "Request APPROVED. Discount is now active."
    else:
        op_request.status = OperationalRequest.RequestStatus.REJECTED
        msg = "Request REJECTED."
        
    op_request.save()
    
    return JsonResponse({
        "request_id": op_request.id,
        "new_status": op_request.status,
        "manager_action": msg
    })





def requests_list(request):
    requests = OperationalRequest.objects.select_related('branch').order_by('-created_at')
    return render(request, 'operations/requests.html', {'requests': requests})




# ... (اترك الدوال السابقة كما هي)

def chart_data_api(request):
    # نجمع البيانات: اسم الفرع + مجموع الهدر المتوقع
    # نأخذ أعلى 5 فروع فقط
    reports = WasteReport.objects.values('branch__name').annotate(
        total_waste=Sum('total_waste_value')
    ).order_by('-total_waste')[:5]

    data = {
        'labels': [item['branch__name'] for item in reports],
        'values': [item['total_waste'] for item in reports]
    }
    
    return JsonResponse(data)
# apps/operations/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404 , render , redirect
from django.contrib.auth import get_user_model
from apps.core.models import Branch
from .models import OperationalRequest
from apps.analytics.models import WasteReport
from django.db.models import Sum


User = get_user_model()

# 1. قائمة التقارير / الطلبات
def requests_list(request):
    from .forms import OperationalRequestForm # استيراد الفورم
    
    # فلترة النتائج حسب الصلاحية
    if request.user.role == 'manager' or request.user.is_superuser:
        # المدير العام يشوف كل شيء
        requests = OperationalRequest.objects.select_related('branch').order_by('-created_at')
        is_manager = True
    elif hasattr(request.user, 'managed_branch'):
        # مدير الفرع يشوف طلباته فقط
        requests = OperationalRequest.objects.filter(branch=request.user.managed_branch).order_by('-created_at')
        is_manager = False
    else:
        requests = OperationalRequest.objects.none()
        is_manager = False

    context = {
        'requests': requests,
        'request_form': OperationalRequestForm(),
        'is_manager': is_manager
    }
    return render(request, 'operations/requests.html', context)

# 2. رفع تقرير جديد (لمدراء الفروع)
def create_request_view(request):
    from .forms import OperationalRequestForm
    from django.contrib import messages
    
    if request.method == 'POST':
        form = OperationalRequestForm(request.POST)
        if form.is_valid():
            try:
                # التأكد أن المستخدم مدير فرع
                branch = request.user.managed_branch
                
                op_request = form.save(commit=False)
                op_request.branch = branch
                op_request.submitted_by = request.user
                op_request.status = 'PENDING'
                op_request.save()
                
                messages.success(request, "تم رفع التقرير للإدارة بنجاح ✅")
            except AttributeError:
                messages.error(request, "عذراً، يجب أن تكون مديراً لفرع لرفع التقارير.")
        else:
            messages.error(request, "يرجى التحقق من البيانات.")
            
    return redirect('operations:requests_list')

# 3. معالجة الطلب (للمدير العام)
def review_request(request, request_id, action):
    # التحقق من صلاحية المدير
    if not (request.user.role == 'manager' or request.user.is_superuser):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    op_request = get_object_or_404(OperationalRequest, id=request_id)
    
    # حفظ رد المدير إذا وجد
    manager_response = request.POST.get('manager_response')
    if manager_response:
        op_request.manager_response = manager_response

    if action == 'approve':
        op_request.status = OperationalRequest.RequestStatus.APPROVED
        msg = "Approved"
    elif action == 'reject': # تصحيح الاسم ليكون consistent
        op_request.status = OperationalRequest.RequestStatus.REJECTED
        msg = "Rejected"
    else:
         msg = "Updated"
        
    op_request.save()
    
    return JsonResponse({
        "request_id": op_request.id,
        "new_status": op_request.status,
        "manager_response": op_request.manager_response
    })




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
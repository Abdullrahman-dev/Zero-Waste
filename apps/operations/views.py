# apps/operations/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404 , render , redirect
from django.contrib.auth import get_user_model
from apps.core.models import Branch, RestaurantCompany
from .models import OperationalRequest
from apps.analytics.models import WasteReport
from django.db.models import Sum


User = get_user_model()

# 1. قائمة التقارير / الطلبات
def requests_list(request):
    from .forms import OperationalRequestForm # استيراد الفورم
    
    # فلترة النتائج حسب الصلاحية
    # فلترة النتائج حسب الصلاحية
    if request.user.role == 'manager':
        # المدير العام يشوف فقط طلبات شركته
        if hasattr(request.user, 'managed_company'):
            requests = OperationalRequest.objects.filter(branch__company=request.user.managed_company).select_related('branch').order_by('-created_at')
        else:
             requests = OperationalRequest.objects.none()
        is_manager = True
    elif request.user.is_superuser:
         # السوبر يوزر يشوف الكل (أو يمكننا إخفاؤه حسب الرغبة، لكن للأغراض التقنية يبقى)
         requests = OperationalRequest.objects.select_related('branch').order_by('-created_at')
         is_manager = True
    elif hasattr(request.user, 'managed_branch'):
        # مدير الفرع يشوف طلباته فقط
        requests = OperationalRequest.objects.filter(branch=request.user.managed_branch).order_by('-created_at')
        is_manager = False
    else:
        requests = OperationalRequest.objects.none()
        is_manager = False

    # --- فلترة الحالة (Status Filter) ---
    status_filter = request.GET.get('status', 'PENDING')
    active_status = status_filter

    if status_filter != 'ALL':
        requests = requests.filter(status=status_filter)
    
    # --- الفلاتر المتقدمة (الشركة والفرع) ---
    companies = None
    branches = None
    selected_company = request.GET.get('company_id')
    selected_branch = request.GET.get('branch_id')

    # Sanitize inputs to prevent 'None' string or non-digit crashes
    if selected_company and (selected_company == 'None' or not selected_company.isdigit()):
        selected_company = None
    
    if selected_branch and (selected_branch == 'None' or not selected_branch.isdigit()):
        selected_branch = None

    # تجهيز القوائم (Dropdowns)
    if request.user.is_superuser:
        companies = RestaurantCompany.objects.all()
        # إذا تم اختيار شركة، نجلب فروعها فقط، وإلا نجلب كل الفروع (أو نتركها فارغة حسب التصميم)
        if selected_company:
            branches = Branch.objects.filter(company_id=selected_company)
        else:
            branches = Branch.objects.all()
            
    elif request.user.role == 'manager' and hasattr(request.user, 'managed_company'):
        branches = request.user.managed_company.branches.all()

    # تطبيق الفلترة على QuerySet
    if selected_company and selected_company != 'None' and selected_company.isdigit() and request.user.is_superuser:
        requests = requests.filter(branch__company_id=selected_company)
        
    if selected_branch and selected_branch != 'None' and selected_branch.isdigit():
        requests = requests.filter(branch_id=selected_branch)
    # ------------------------------------

    # التحقق مما إذا كان هناك طلب مسبق (pre-filled) من التنبيهات
    initial_data = {}
    if 'type' in request.GET:
        initial_data['type'] = request.GET['type']
    if 'details' in request.GET:
        initial_data['details'] = request.GET['details']
    if 'branch_id' in request.GET:
        initial_data['branch'] = request.GET['branch_id']

    context = {
        'requests': requests,
        'request_form': OperationalRequestForm(initial=initial_data, user=request.user),
        'is_manager': is_manager,
        'active_status': active_status,
        'companies': companies,
        'branches': branches,
        'selected_company': selected_company,
        'selected_branch': selected_branch,
    }
    return render(request, 'operations/requests.html', context)

# 2. رفع تقرير جديد
def create_request_view(request):
    from .forms import OperationalRequestForm
    from django.contrib import messages
    
    if request.method == 'POST':
        form = OperationalRequestForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                op_request = form.save(commit=False)
                op_request.submitted_by = request.user
                op_request.status = 'PENDING'

                # تحديد الفرع حسب الصلاحية
                if hasattr(request.user, 'managed_branch'):
                    op_request.branch = request.user.managed_branch
                elif request.user.role == 'manager' and op_request.branch:
                    # المدير اختار الفرع من القائمة
                    pass 
                else:
                    messages.error(request, "عذراً، يجب تحديد الفرع.")
                    return redirect('operations:requests_list')

                op_request.save()
                messages.success(request, "تم رفع التقرير بنجاح ✅")
            except Exception as e:
                 messages.error(request, f"حدث خطأ: {e}")
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
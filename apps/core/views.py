# apps/core/views.py
from django.shortcuts import render, redirect
from django.db.models import Sum
from django.http import JsonResponse # 👈 ضروري جداً عشان الـ API يشتغل
from apps.core.models import Branch
from apps.analytics.models import WasteReport
from apps.operations.models import OperationalRequest
from .models import Branch

# 1. الدالة الرئيسية (أبقيناها كما هي dashboard_home)
# 1. الدالة الرئيسية (Router) - تحدد أي داشبورد يظهر حسب الدور
def dashboard_router(request):
    if not request.user.is_authenticated:
        # إذا لم يسجل الدخول، نوجهه لصفحة الدخول
        from django.shortcuts import redirect
        return redirect('login') # تأكد أن اسم الـ url هو 'login'

    # 1. Platform Admin (الآدمن العام)
    if request.user.is_superuser:
        return _admin_dashboard(request)
    
    # 2. General Manager (مدير شركة)
    elif request.user.role == 'manager':
        return _company_dashboard(request)
        
    # 3. Branch Manager (مدير فرع)
    elif request.user.role == 'branch_manager':
        return _branch_dashboard(request)
    
    else:
        # حالة احتياطية لو يوزر بدون دور
        return render(request, 'core/dashboard_empty.html', {})

# --- Private Views (Internal Use) ---

def _admin_dashboard(request):
    """
    SaaS Admin Dashboard: Shows list of clients (Restaurant Companies) and subscription status.
    """
    from apps.core.models import RestaurantCompany
    from .forms import CompanyForm # استيراد الفورم
    
    companies = RestaurantCompany.objects.select_related('manager').all().order_by('-created_at')
    total_companies = companies.count()
    active_subscriptions = companies.filter(subscription_status=True).count()
    
    # محاكاة لإجمالي الإيرادات (لاحقاً يمكن ربطها بنظام دفع حقيقي)
    total_revenue = active_subscriptions * 299 # افتراض سعر الاشتراك 299

    context = {
        'user_role': 'SaaS Administrator',
        'companies': companies,
        'total_companies': total_companies,
        'active_subscriptions': active_subscriptions,
        'total_revenue': total_revenue,
        'company_form': CompanyForm(), # تمرير الفورم الفارغ للنافذة المنبثقة
    }
    return render(request, 'core/dashboard_saas_admin.html', context)

def add_company_view(request):
    from .forms import CompanyForm
    from django.contrib import messages
    
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save()
            messages.success(request, f"تم إضافة شركة '{company.name}' بنجاح!")
        else:
            messages.error(request, "حدث خطأ أثناء إضافة الشركة. يرجى التحقق من البيانات.")
            
    return redirect('core:dashboard') # العودة للداشبورد دائماً

def _company_dashboard(request):
    """
    Main Manager Dashboard: Full access to company stats and management.
    """
    try:
        company = request.user.managed_company
    except:
        return render(request, 'core/dashboard_empty.html', {'error': 'No company assigned'})

    branches = company.branches.all()
    
    # إحصائيات عامة
    total_branches = branches.count()
    
    # تجميع الهدر من كل الفروع
    latest_reports = WasteReport.objects.filter(branch__in=branches).select_related('branch').order_by('-generated_date')[:5]
    total_potential_loss = WasteReport.objects.filter(branch__in=branches).aggregate(sum=Sum('total_waste_value'))['sum'] or 0
    pending_requests = OperationalRequest.objects.filter(branch__in=branches, status='PENDING').order_by('-created_at')

    context = {
        'user_role': f"General Manager - {company.name}",
        'company': company,
        'total_branches': total_branches,
        'total_potential_loss': total_potential_loss,
        'latest_reports': latest_reports,
        'pending_requests': pending_requests,
        'is_manager': True, # هذا المتغير يفتح الأزرار الإدارية في القالب
    }
    return render(request, 'core/dashboard_company.html', context)

def _branch_dashboard(request):
    """
    Branch Dashboard: Similar to Main Dashboard but restricted to one branch and no admin actions.
    """
    try:
        branch = request.user.managed_branch
    except:
        return render(request, 'core/dashboard_empty.html', {'error': 'No branch assigned'})

    # إحصائيات الفرع فقط
    latest_reports = WasteReport.objects.filter(branch=branch).order_by('-generated_date')[:5]
    total_potential_loss = WasteReport.objects.filter(branch=branch).aggregate(sum=Sum('total_waste_value'))['sum'] or 0
    
    # ملاحظة: في التصميم الجديد، مدير الفرع يشوف نفس شكل الداشبورد لكن بياناته محدود
    # لن نظهر "طلباتي" في الويدجت الرئيسي لتوحيد الشكل، بل سنضعها في قسم جانبي أو صفحة مستقلة
    # لكن سنمررها في الـ context
    my_requests = OperationalRequest.objects.filter(branch=branch).order_by('-created_at')[:5]

    context = {
        'user_role': f"Branch Manager - {branch.name}",
        'branch': branch, 
        'total_branches': 1, # دائما 1 في نظر مدير الفرع
        'total_potential_loss': total_potential_loss,
        'latest_reports': latest_reports,
        'pending_requests': [], # مدير الفرع لا يوافق على طلبات، لذا القائمة فارغة
        'my_requests': my_requests,
        'is_manager': False, # هذا يخفي أزرار الإضافة والتعديل
    }
    # نستخدم نفس قالب الشركة لتوحيد الشكل، لكن مع قيود الصلاحيات
    return render(request, 'core/dashboard_company.html', context)


# 2. دالة الرسم البياني (هذه هي الإضافة الجديدة فقط)
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

# صفحة عرض الفروع
def branch_list(request):
    from .forms import BranchForm # استيراد الفورم

    # التأكد أن المستخدم مدير شركة لجلب فروعه فقط
    try:
        company = request.user.managed_company
        branches = Branch.objects.filter(company=company)
    except:
        # إذا كان سوبر يوزر، نعرض كل الفروع (لأغراض الادمن)
        if request.user.is_superuser:
            branches = Branch.objects.all()
        else:
            branches = Branch.objects.none()

    context = {
        'branches': branches,
        'title': 'إدارة الفروع',
        'branch_form': BranchForm(), # تمرير الفورم للمودال
    }
    return render(request, 'core/branch_list.html', context)

def add_branch_view(request):
    from .forms import BranchForm
    from django.contrib import messages
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if request.method == 'POST':
        # 🛡️ تحقق أمني إضافي (Authorization)
        if not (request.user.is_superuser or request.user.role == 'manager'):
            messages.error(request, "ليس لديك صلاحية للقيام بهذا الإجراء.")
            return redirect('core:branch_list')

        form = BranchForm(request.POST)
        if form.is_valid():
            branch = form.save(commit=False)
            
            # ... منطق إنشاء المستخدم الجديد ...
            if form.cleaned_data.get('create_new_manager'):
                username = form.cleaned_data.get('new_manager_username')
                password = form.cleaned_data.get('new_manager_password')
                
                # إنشاء اليوزر بصلاحية مدير فرع
                new_manager = User.objects.create_user(username=username, password=password, role='branch_manager')
                branch.manager = new_manager
                messages.success(request, f"تم إنشاء حساب للمدير '{username}' بنجاح.")

            # تعيين الشركة تلقائياً
            if hasattr(request.user, 'managed_company'):
                branch.company = request.user.managed_company
                branch.save()
                messages.success(request, f"تم إضافة فرع '{branch.name}' بنجاح!")
            else:
                messages.error(request, "عذراً، يجب أن تكون مدير شركة لإضافة فروع.")
        else:
            # عرض الأخطاء (مثل اسم المستخدم مكرر)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            
    return redirect('core:branch_list')
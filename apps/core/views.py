# apps/core/views.py
from django.shortcuts import render
from django.db.models import Sum
from django.http import JsonResponse # 👈 ضروري جداً عشان الـ API يشتغل
from apps.core.models import Branch
from apps.analytics.models import WasteReport
from apps.operations.models import OperationalRequest
from .models import Branch

# 1. الدالة الرئيسية (أبقيناها كما هي dashboard_home)
def dashboard_home(request):
    # إحصائيات عامة
    total_branches = Branch.objects.count()
    
    # تحذيرات الذكاء الاصطناعي (أحدث 5 تقارير)
    latest_reports = WasteReport.objects.select_related('branch').order_by('-generated_date')[:5]
    
    # حساب مجموع الهدر (مع حماية ضد القيم الفارغة)
    total_potential_loss = WasteReport.objects.aggregate(sum=Sum('total_waste_value'))['sum']
    if total_potential_loss is None:
        total_potential_loss = 0
    
    # الطلبات التشغيلية المعلقة
    pending_requests = OperationalRequest.objects.filter(status='PENDING').order_by('-created_at')

    context = {
        'total_branches': total_branches,
        'total_potential_loss': total_potential_loss,
        'latest_reports': latest_reports,
        'pending_requests': pending_requests,
    }
    
    return render(request, 'core/dashboard.html', context)


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
    branches = Branch.objects.all()
    context = {
        'branches': branches,
        'title': 'إدارة الفروع'
    }
    return render(request, 'core/branch_list.html', context)
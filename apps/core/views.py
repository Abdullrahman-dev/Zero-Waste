# apps/core/views.py
from django.shortcuts import render
from django.db.models import Sum, Count
from apps.core.models import Branch, RestaurantCompany
from apps.analytics.models import WasteReport
from apps.operations.models import OperationalRequest

def dashboard_home(request):
    # 1. إحصائيات عامة
    total_branches = Branch.objects.count()
    
    # 2. تحذيرات الذكاء الاصطناعي (أحدث 5 تقارير)
    latest_reports = WasteReport.objects.order_by('-generated_date')[:5]
    total_potential_loss = WasteReport.objects.aggregate(Sum('total_waste_value'))['total_waste_value__sum'] or 0
    
    # 3. الطلبات التشغيلية المعلقة (تحتاج موافقة)
    pending_requests = OperationalRequest.objects.filter(
        status=OperationalRequest.RequestStatus.PENDING
    ).order_by('-created_at')

    context = {
        'total_branches': total_branches,
        'total_potential_loss': total_potential_loss,
        'latest_reports': latest_reports,
        'pending_requests': pending_requests,
    }
    
    return render(request, 'core/dashboard.html', context)
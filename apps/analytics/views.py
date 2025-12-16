# apps/analytics/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404 , render
from apps.core.models import Branch
from .services import AIEngine

def generate_waste_report(request, branch_id):
    # 1. تحديد الفرع
    branch = get_object_or_404(Branch, id=branch_id)
    
    # 2. تشغيل محرك الذكاء
    engine = AIEngine()
    report, message = engine.analyze_and_generate_report(branch)

    # 3. إرجاع النتيجة
    if report:
        return JsonResponse({
            'status': 'success',
            'report_id': report.id,
            'total_waste_value': report.total_waste_value,
            'analysis': report.ai_analysis
        })
    else:
        return JsonResponse({
            'status': 'safe',
            'message': message
        })
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .utils import get_branch_context
from .predictor import get_ai_insights
from apps.analytics.models import WasteReport
from apps.core.models import Branch
import json

@require_GET
def predict_waste_view(request, branch_id):
    
    # 1. Gather Data

    context_data = get_branch_context(branch_id)
    if not context_data:
        return JsonResponse({"error": "Branch not found or no data"}, status=404)
    
        
    # 2. Call AI Engine

    ai_result = get_ai_insights(context_data)
    
    if "error" in ai_result:
        return JsonResponse(ai_result, status=500)
    

    # 3. Save Report

    try:
        branch = Branch.objects.get(id=branch_id)
        
        financial_impact = ai_result.get('financial_impact', {})
        total_risk = financial_impact.get('total_risk_value', 0.0)
        
        try:
            if isinstance(total_risk, str):
                total_risk = float(total_risk.replace(' ر.س', '').replace('SAR', '').replace(',', '').strip())
            else:
                total_risk = float(total_risk)
        except (ValueError, TypeError):
            total_risk = 0.0

        WasteReport.objects.create(
            branch=branch,
            total_waste_value=total_risk,
            ai_analysis=json.dumps(ai_result)
        )
    except Exception as e:
        print(f"Failed to save report: {e}")

    return JsonResponse(ai_result)

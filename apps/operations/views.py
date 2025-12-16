# apps/operations/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404 , render
from django.contrib.auth import get_user_model
from apps.core.models import Branch
from .models import OperationalRequest


User = get_user_model()

# 1. محاكاة: مدير الفرع يرسل طلب عرض خاص
def create_offer_request(request, branch_id):
    branch = get_object_or_404(Branch, id=branch_id)
    
    # نفترض أن المستخدم رقم 1 هو المدير (للتجربة السريعة)
    # في الواقع نستخدم request.user
    manager = User.objects.first() 
    
    new_request = OperationalRequest.objects.create(
        submitted_by=manager,
        branch=branch,
        type="URGENT_PROMO",
        details="AI Alert: Burger expiring in 4 days. Requesting 50% Discount approval.",
        status=OperationalRequest.RequestStatus.PENDING
    )
    
    return JsonResponse({
        "status": "submitted",
        "request_id": new_request.id,
        "message": "Operational request sent to General Manager successfully."
    })

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
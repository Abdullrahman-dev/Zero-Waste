from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.db.models import Sum, Count, F, ExpressionWrapper, DecimalField
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta
from apps.core.models import Branch
from apps.inventory.models import Product
from .services import AIEngine
from .models import WasteReport, WasteLog
from apps.ai_engine.predictor import get_ai_insights

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
    

def analytics_dashboard(request):
    reports = WasteReport.objects.select_related('branch').order_by('-generated_date')
    return render(request, 'analytics/reports.html', {'reports': reports})

def log_waste(request):
    """
    تسجيل هدر جديد مع خصم الكمية من المخزون تلقائياً
    """
    from django.contrib import messages
    from django.shortcuts import redirect
    from apps.inventory.models import StockItem
    from .forms import WasteLogForm
    
    # التحقق من الصلاحيات
    if not request.user.is_authenticated:
        return redirect('login')
        
    branch = None
    stock_item_id = request.GET.get('stock_id')
    
    # تحسين منطق تحديد الصلاحية: إذا كان مديراً للشركة، فله صلاحية على كل الفروع
    if request.user.role == 'manager' and hasattr(request.user, 'managed_company'):
        if stock_item_id:
            try:
                stock_item = StockItem.objects.get(id=stock_item_id)
                if stock_item.branch.company == request.user.managed_company:
                    branch = stock_item.branch
            except StockItem.DoesNotExist:
                from django.contrib import messages
                messages.error(request, "عذراً، لم يتم العثور على هذا العنصر في المخزون (ربما تم استهلاكه أو حذفه).")
                return redirect('inventory:inventory_list')
    
    # إذا لم تتحدد كمدير شركة، نستخدم الفرع المدار مباشرة (لمدراء الفروع)
    if not branch and hasattr(request.user, 'managed_branch') and request.user.managed_branch:
        branch = request.user.managed_branch

    # التحقق النهائي من وجود الفرع والصلاحية
    if not branch:
         from django.contrib import messages
         if hasattr(request.user, 'managed_company'):
             messages.error(request, "تنبيه: كمدير شركة، يرجى اختيار 'تسجيل هدر' من صفحة المخزون لفرع محدد.")
             return redirect('inventory:inventory_list')
         else:
             messages.error(request, "عذراً، ليس لديك صلاحية الوصول لهذه الصفحة.")
             return redirect('core:dashboard')

    initial_data = {}
    if stock_item_id:
        try:
            stock_item = StockItem.objects.get(id=stock_item_id, branch=branch)
            initial_data = {'product': stock_item.product, 'quantity': stock_item.quantity}
        except StockItem.DoesNotExist:
            from django.contrib import messages
            messages.error(request, "تنبيه: عنصر المخزون المختار غير متوفر أو لا يتبع لفرعك.")
            return redirect('inventory:inventory_list')

    if request.method == 'POST':
        form = WasteLogForm(request.POST, branch=branch)
        if form.is_valid():
            waste_entry = form.save(commit=False)
            waste_entry.branch = branch
            waste_entry.submitted_by = request.user
            
            product = waste_entry.product
            quantity_to_remove = waste_entry.quantity
            
            stock_items = list(StockItem.objects.filter(branch=branch, product=product).order_by('expiry_date'))
            total_available = sum(item.quantity for item in stock_items)
            
            if total_available < quantity_to_remove:
                messages.error(request, f"خطأ: الكمية المراد هدرها أكبر من المتوفر!")
            else:
                remaining = quantity_to_remove
                for item in stock_items:
                    if remaining <= 0: break
                    if item.quantity >= remaining:
                        item.quantity -= remaining
                        item.save()
                        remaining = 0
                    else:
                        remaining -= item.quantity
                        item.quantity = 0
                        item.save()
                waste_entry.save()
                messages.success(request, f"تم تسجيل الهدر بنجاح.")
                return redirect('analytics:waste_list') 
    else:
        form = WasteLogForm(branch=branch, initial=initial_data)
    
    return render(request, 'analytics/log_waste.html', {'form': form, 'title': 'تسجيل هدر جديد 🗑️'})

def waste_list(request):
    logs = WasteLog.objects.select_related('product', 'branch', 'submitted_by').order_by('-created_at')
    
    # تحسين الفلترة: مدير الشركة يرى جميع فروع شركته
    if request.user.role == 'manager' and hasattr(request.user, 'managed_company'):
        logs = logs.filter(branch__company=request.user.managed_company)
    elif hasattr(request.user, 'managed_branch') and request.user.managed_branch:
        logs = logs.filter(branch=request.user.managed_branch)
        
    return render(request, 'analytics/waste_list.html', {'logs': logs})

def reduction_suggestions(request):
    """
    صفحة "تقليل الخسائر" - تعطي نصائح للشراء للأسبوع القادم
    """
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('login') 
        
    company = None
    if hasattr(request.user, 'managed_company'):
        company = request.user.managed_company
    elif hasattr(request.user, 'managed_branch') and request.user.managed_branch:
         company = request.user.managed_branch.company
    
    # Analyze high waste items (Top 10)
    # We look at the last 30 days to get a trend
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    high_waste_items = WasteLog.objects.filter(
        created_at__gte=thirty_days_ago
    )
    
    if company:
        high_waste_items = high_waste_items.filter(branch__company=company)
        
    high_waste_items = high_waste_items.values(
        'product__name', 'product__unit', 'product__cost_price'
    ).annotate(
        total_qty=Sum('quantity'),
        total_loss=Sum(ExpressionWrapper(F('quantity') * F('product__cost_price'), output_field=DecimalField()))
    ).order_by('-total_loss')[:10]
    
    # Prepare Data for AI
    items_data = []
    for item in high_waste_items:
        items_data.append({
            'name': item['product__name'],
            'unit': item['product__unit'],
            'total_qty': float(item['total_qty']),
            'total_loss': float(item['total_loss'])
        })
        
    context = {
        'branch_name': company.name,
        'analysis_type': 'purchasing_advice',
        'high_waste_items': items_data
    }
    
    # Call AI
    ai_result = get_ai_insights(context)
    suggestions = ai_result.get('suggestions', [])
        
    return render(request, 'analytics/reduction_suggestions.html', {'suggestions': suggestions})

# --- Advanced Analytics APIs ---

def analytics_stats_api(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    # 1. Top Wasted Products
    top_wasted = WasteLog.objects.values('product__name').annotate(
        estimated_loss=Sum(ExpressionWrapper(F('quantity') * F('product__cost_price'), output_field=DecimalField()))
    ).order_by('-estimated_loss')[:5]

    # 2. Monthly Trend
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_loss = WasteReport.objects.filter(
        generated_date__gte=six_months_ago
    ).annotate(
        month=TruncMonth('generated_date')
    ).values('month').annotate(
        total_loss=Sum('total_waste_value')
    ).order_by('month')

    data = {
        'top_products': {
            'labels': [item['product__name'] for item in top_wasted],
            'values': [float(item['estimated_loss'] or 0) for item in top_wasted]
        },
        'monthly_trend': {
            'labels': [item['month'].strftime('%Y-%m') for item in monthly_loss],
            'values': [float(item['total_loss'] or 0) for item in monthly_loss]
        }
    }
    return JsonResponse(data)

def magic_ai_advice_api(request):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)

        company = None
        if hasattr(request.user, 'managed_company'):
            company = request.user.managed_company
        elif hasattr(request.user, 'managed_branch') and request.user.managed_branch:
             company = request.user.managed_branch.company
        
        if not company:
            return JsonResponse({'error': 'No company found'}, status=400)

        # 1. Check for specific Branch ID
        target_branch = None
        branch_id = request.GET.get('branch_id')
        
        if branch_id:
            from apps.core.models import Branch
            target_branch = get_object_or_404(Branch, id=branch_id)
            # Security Check: Ensure branch belongs to the managed company
            if target_branch.company != company:
                return JsonResponse({'error': 'Unauthorized branch access'}, status=403)

        # 2. Filter Data (Company-wide OR Specific Branch)
        if target_branch:
             logs = WasteLog.objects.filter(branch=target_branch).order_by('-created_at')[:20]
             stats_logs_count = WasteReport.objects.filter(branch=target_branch).count()
             total_loss_decimal = WasteReport.objects.filter(branch=target_branch).aggregate(Sum('total_waste_value'))['total_waste_value__sum'] or 0
             analysis_scope_name = target_branch.name
        else:
             logs = WasteLog.objects.filter(branch__company=company).order_by('-created_at')[:20]
             stats_logs_count = WasteReport.objects.filter(branch__company=company).count()
             total_loss_decimal = WasteReport.objects.filter(branch__company=company).aggregate(Sum('total_waste_value'))['total_waste_value__sum'] or 0
             analysis_scope_name = company.name

        logs_summary = [f"- {l.product.name}: {l.quantity} {l.product.unit} at {l.created_at.date()}" for l in logs]

        context = {
            'branch_name': analysis_scope_name,
            'analysis_type': 'historical_strategic_advice',
            'historical_logs': logs_summary,
            'stats': {
                'total_reports': stats_logs_count,
                'total_loss': float(total_loss_decimal)
            }
        }

        advice_result = get_ai_insights(context)
        return JsonResponse(advice_result)
        
    except Exception as e:
        import traceback
        print(traceback.format_exc()) # Log to console
        return JsonResponse({'error': f"Internal Error: {str(e)}"}, status=500)
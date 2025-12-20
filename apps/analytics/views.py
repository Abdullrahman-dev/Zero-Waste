# apps/analytics/views.py
from django.http import JsonResponse
from django.shortcuts import get_object_or_404 , render
from apps.core.models import Branch
from .services import AIEngine
from .models import WasteReport

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
        
    # تحديد الفرع (لمدير الفرع أو السوبر فايزر)
    branch = None
    stock_item_id = request.GET.get('stock_id')
    
    if hasattr(request.user, 'managed_branch'):
        branch = request.user.managed_branch
    elif hasattr(request.user, 'managed_company'):
        # للمدير العام: نحاول استنتاج الفرع من عنصر المخزون المختار
        if stock_item_id:
            stock_item = get_object_or_404(StockItem, id=stock_item_id)
            # تأكد أن العنصر يتبع لشركة المدير
            if stock_item.branch.company == request.user.managed_company:
                branch = stock_item.branch
    
    # إذا لم يتم تحديد الفرع حتى الآن، نوقف العملية (مؤقتاً للتبسيط)
    if not branch:
         if hasattr(request.user, 'managed_company'):
             messages.error(request, "تنبيه: كمدير شركة، يفضل تسجيل الهدر من خلال زر 'تدوير/هدر' في صفحة مخزون الفرع المحدد لضمان الدقة.")
             return redirect('inventory:inventory_list')
         else:
             messages.error(request, "عذراً، ليس لديك صلاحية الوصول.")
             return redirect('core:dashboard')

    # التحقق مما إذا كان هناك عنصر مخزون محدد مسبقاً (قادم من صفحة المخزون)
    initial_data = {}
    stock_item_id = request.GET.get('stock_id')
    if stock_item_id:
        stock_item = get_object_or_404(StockItem, id=stock_item_id, branch=branch)
        initial_data = {
            'product': stock_item.product,
            'quantity': stock_item.quantity
        }

    if request.method == 'POST':
        form = WasteLogForm(request.POST, branch=branch)
        if form.is_valid():
            waste_entry = form.save(commit=False)
            waste_entry.branch = branch
            waste_entry.submitted_by = request.user
            
            # --- المنطق الذكي: خصم الكمية من المخزون ---
            product = waste_entry.product
            quantity_to_remove = waste_entry.quantity
            
            # إذا كان التحويل من عنصر مخزون محدد، نبدأ به أولاً
            specific_stock_item = None
            if stock_item_id:
                try:
                    specific_stock_item = StockItem.objects.get(id=stock_item_id, branch=branch, product=product)
                except StockItem.DoesNotExist:
                    pass

            stock_items = list(StockItem.objects.filter(branch=branch, product=product).order_by('expiry_date'))
            
            # إذا كان لدينا عنصر محدد، نضعه في بداية القائمة للخصم منه أولاً
            if specific_stock_item and specific_stock_item in stock_items:
                stock_items.remove(specific_stock_item)
                stock_items.insert(0, specific_stock_item)
            
            # حساب إجمالي المتوفر
            total_available = sum(item.quantity for item in stock_items)
            
            if total_available < quantity_to_remove:
                messages.error(request, f"خطأ: الكمية المراد هدرها ({quantity_to_remove}) أكبر من المتوفر في المخزون ({total_available})!")
            else:
                # الخصم من الدفعات حسب الأقدمية (FIFO) أو المحدد أولاً
                remaining = quantity_to_remove
                for item in stock_items:
                    if remaining <= 0:
                        break
                    
                    if item.quantity >= remaining:
                        item.quantity -= remaining
                        item.save()
                        remaining = 0
                    else:
                        remaining -= item.quantity
                        item.quantity = 0
                        item.save()
                
                waste_entry.save()
                messages.success(request, f"تم تسجيل الهدر ({product.name}) وخصم الكمية من المخزون بنجاح.")
                return redirect('analytics:waste_list') 
    else:
        form = WasteLogForm(branch=branch, initial=initial_data)
    
    context = {
        'form': form,
        'title': 'تسجيل هدر جديد 🗑️'
    }
    return render(request, 'analytics/log_waste.html', context)
    
def waste_list(request):
    """عرض سجل الهدر"""
    from .models import WasteLog
    
    # الفلترة حسب الصلاحية
    logs = WasteLog.objects.select_related('product', 'branch', 'submitted_by').order_by('-created_at')
    
    if hasattr(request.user, 'managed_branch'):
        logs = logs.filter(branch=request.user.managed_branch)
    elif hasattr(request.user, 'managed_company'):
        logs = logs.filter(branch__company=request.user.managed_company)
        
    return render(request, 'analytics/waste_list.html', {'logs': logs})
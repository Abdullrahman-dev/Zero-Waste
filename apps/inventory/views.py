from django.shortcuts import render, redirect ,get_object_or_404
from .models import StockItem
from datetime import date
from .forms import ProductForm, StockItemForm 


from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def inventory_list(request):
    # 🛡️ العزل: نستخدم select_related للأداء العالي مع الفلترة الأمنية
    stock_items = StockItem.objects.select_related('product', 'branch').order_by('expiry_date')

    # 1. إذا كان مدير شركة: يشوف مخزون كل فروعه
    if request.user.role == 'manager' and hasattr(request.user, 'managed_company'):
        stock_items = stock_items.filter(branch__company=request.user.managed_company)
    
    # 2. إذا كان مدير فرع: يشوف مخزون فرعه فقط
    elif request.user.role == 'branch_manager' and hasattr(request.user, 'managed_branch'):
        stock_items = stock_items.filter(branch=request.user.managed_branch)
        
    # 3. إذا كان سوبر يوزر: يشوف الكل (إلا إذا أردنا حجبه أيضاً)
    elif not request.user.is_superuser:
         stock_items = stock_items.none() # منع الوصول لأي شخص آخر

    context = {
        'stock_items': stock_items, 
        'today': date.today(),
    }
    return render(request, 'inventory/list.html', context)

# دالة إضافة منتج
@login_required(login_url='login')
def add_product(request):
    # 🛡️ الحماية: المسموح فقط للمدير العام أو السوبر يوزر
    if not (request.user.is_superuser or request.user.role == 'manager'):
        from django.contrib import messages
        messages.error(request, "عذراً، إضافة المنتجات من صلاحيات الإدارة العليا فقط.")
        return redirect('inventory:inventory_list')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            if hasattr(request.user, 'managed_company'):
                product.company = request.user.managed_company
            product.save()
            return redirect('inventory:inventory_list')
    else:
        form = ProductForm()
    
    return render(request, 'inventory/add_product.html', {'form': form, 'title': 'إضافة منتج جديد'})

# دالة إضافة مخزون
@login_required(login_url='login')
def add_stock_item(request):
    if request.method == 'POST':
        form = StockItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:inventory_list')  # ✅ تم التعديل هنا
    else:
        form = StockItemForm()
    
    return render(request, 'inventory/add_product.html', {'form': form, 'title': 'إضافة عنصر مخزون'})

# ✏️ دالة تعديل المخزون
@login_required(login_url='login')
def edit_stock_item(request, pk):
    item = get_object_or_404(StockItem, pk=pk) # جبنا العنصر المطلوب
    
    if request.method == 'POST':
        form = StockItemForm(request.POST, instance=item) # مررنا instance عشان يعبي البيانات القديمة
        if form.is_valid():
            form.save()
            return redirect('inventory:inventory_list')
    else:
        form = StockItemForm(instance=item) # عبئ النموذج بالبيانات الحالية
    
    return render(request, 'inventory/add_product.html', {
        'form': form, 
        'title': f'تعديل: {item.product.name}'
    })

# 🗑️ دالة حذف المخزون
def delete_stock_item(request, pk):
    item = get_object_or_404(StockItem, pk=pk)
    
    if request.method == 'POST':
        item.delete()
        return redirect('inventory:inventory_list')
        
    return render(request, 'inventory/confirm_delete.html', {'item': item})
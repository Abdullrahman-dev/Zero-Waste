from django.shortcuts import render, redirect ,get_object_or_404
from .models import StockItem
from datetime import date
from .forms import ProductForm, StockItemForm 


def inventory_list(request):
    # نستخدم select_related للأداء العالي
    stock_items = StockItem.objects.select_related('product', 'branch').order_by('expiry_date')
    
    context = {
        'stock_items': stock_items, 
        'today': date.today(),
    }
    return render(request, 'inventory/list.html', context)

# دالة إضافة منتج
def add_product(request):
    # 🛡️ الحماية: المسموح فقط للمدير العام أو السوبر يوزر
    if not (request.user.is_superuser or request.user.role == 'manager'):
        from django.contrib import messages
        messages.error(request, "عذراً، إضافة المنتجات من صلاحيات الإدارة العليا فقط.")
        return redirect('inventory:inventory_list')

    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:inventory_list')  # ✅ تم التعديل هنا
    else:
        form = ProductForm()
    
    return render(request, 'inventory/add_product.html', {'form': form, 'title': 'إضافة منتج جديد'})

# دالة إضافة مخزون
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
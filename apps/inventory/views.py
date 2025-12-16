# apps/inventory/views.py
from django.shortcuts import render
from .models import StockItem

def inventory_list(request):
    # جلب جميع العناصر مع بيانات المنتج والفرع لتقليل الاستعلامات
    items = StockItem.objects.select_related('product', 'branch').all().order_by('expiry_date')
    
    context = {
        'items': items
    }
    return render(request, 'inventory/list.html', context)
# apps/inventory/views.py
from django.shortcuts import render
from .models import StockItem
from datetime import date

def inventory_list(request):
    # نستخدم select_related عشان يجيب بيانات المنتج والفرع في "ضربة واحدة" للداتابيس (أداء أسرع)
    stock_items = StockItem.objects.select_related('product', 'branch').order_by('expiry_date')
    
    context = {
        # سميناها stock_items عشان تكون واضحة في ملف HTML
        'stock_items': stock_items, 
        'today': date.today(),
    }
    return render(request, 'inventory/list.html', context)
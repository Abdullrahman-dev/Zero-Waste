from django.contrib import admin
from .models import Product, StockItem

# 1. شاشة إدارة المنتجات (التعريفات)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'category', 'unit')
    search_fields = ('name', 'sku')

# 2. شاشة إدارة المخزون (الكميات والتواريخ)
@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    # لاحظ كيف نعرض اسم المنتج واسم الفرع
    list_display = ('product', 'branch', 'quantity', 'expiry_date', 'batch_id')
    
    # فلترة حسب الفرع وتاريخ الانتهاء
    list_filter = ('branch', 'expiry_date')
    
    # البحث داخل اسم المنتج المرتبط
    search_fields = ('product__name', 'batch_id')
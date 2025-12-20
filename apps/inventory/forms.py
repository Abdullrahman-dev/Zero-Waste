# apps/inventory/forms.py
from django import forms
from .models import Product, StockItem

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'category', 'unit', 'cost_price', 'minimum_quantity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: برجر دجاج'}),
            'sku': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CHK-001'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'unit': forms.Select(attrs={'class': 'form-select'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'minimum_quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }
        labels = {
            'name': 'اسم المنتج',
            'sku': 'رمز SKU',
            'category': 'التصنيف',
            'unit': 'وحدة القياس',
            'cost_price': 'سعر التكلفة',
            'minimum_quantity': 'حد التنبيه (Low Stock)',
        }

class StockItemForm(forms.ModelForm):
    class Meta:
        model = StockItem
        fields = ['product', 'branch', 'quantity', 'expiry_date', 'batch_id']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'batch_id': forms.TextInput(attrs={'class': 'form-control'}),
        }
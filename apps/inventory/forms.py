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
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(StockItemForm, self).__init__(*args, **kwargs)
        if user:
            if hasattr(user, 'managed_company'):
                self.fields['product'].queryset = Product.objects.filter(company=user.managed_company)
                self.fields['branch'].queryset = user.managed_company.branches.all()
            elif hasattr(user, 'managed_branch'):
                # Branch Managers should only add stock to their own branch? Or maybe they don't have this permission?
                # Assuming for now they might, limiting to their branch and company products
                self.fields['product'].queryset = Product.objects.filter(company=user.managed_branch.company)
                self.fields['branch'].queryset = user.managed_company.branches.filter(id=user.managed_branch.id)
                self.fields['branch'].initial = user.managed_branch
                self.fields['branch'].widget.attrs['readonly'] = True # Optional: lock it

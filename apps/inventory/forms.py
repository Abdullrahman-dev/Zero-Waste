from django import forms
from .models import Product, StockItem
from apps.core.models import Branch

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
            try:
                if hasattr(user, 'managed_company'):
                    company = user.managed_company
                    self.fields['product'].queryset = Product.objects.filter(company=company)
                    self.fields['branch'].queryset = company.branches.all()
                elif hasattr(user, 'managed_branch'):
                    branch = user.managed_branch
                    self.fields['product'].queryset = Product.objects.filter(company=branch.company)
                    self.fields['branch'].queryset = branch.company.branches.filter(id=branch.id)
                    self.fields['branch'].initial = branch
                    self.fields['branch'].widget.attrs['readonly'] = True
            except Exception:
                # Fallback for safer error handling (e.g., if user is superuser or data inconsistency)
                # We can choose to show nothing or everything. For safety, let's show nothing or log it.
                # If superuser, maybe show all?
                if user.is_superuser:
                    self.fields['product'].queryset = Product.objects.all()
                    self.fields['branch'].queryset = Branch.objects.all() # Need implicit import or model ref
                else:
                    self.fields['product'].queryset = Product.objects.none()
                    self.fields['branch'].queryset = Product.objects.none() # Empty queryset

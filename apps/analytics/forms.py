from django import forms
from .models import WasteLog
from apps.inventory.models import Product

class WasteLogForm(forms.ModelForm):
    class Meta:
        model = WasteLog
        fields = ['product', 'quantity', 'reason', 'notes']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'reason': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        branch = kwargs.pop('branch', None)
        super().__init__(*args, **kwargs)
        if branch and hasattr(branch, 'company'):
            self.fields['product'].queryset = Product.objects.filter(company=branch.company)

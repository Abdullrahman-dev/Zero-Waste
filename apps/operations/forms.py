from django import forms
from .models import OperationalRequest

class OperationalRequestForm(forms.ModelForm):
    class Meta:
        model = OperationalRequest
        fields = ['type', 'details']
        widgets = {
            'type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نوع التقرير/الطلب'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'اكتب تفاصيل التقرير هنا...'}),
        }
        labels = {
            'type': 'عنوان التقرير',
            'details': 'التفاصيل',
        }

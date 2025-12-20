from django import forms
from .models import OperationalRequest

class OperationalRequestForm(forms.ModelForm):
    class Meta:
        model = OperationalRequest
        fields = ['type', 'details', 'branch']
        widgets = {
            'type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'نوع التقرير/الطلب'}),
            'details': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'اكتب تفاصيل التقرير هنا...'}),
            'branch': forms.Select(attrs={'class': 'form-select', 'style': 'display:none'}), # نخفيه افتراضياً ونظهره للمدير
        }
        labels = {
            'type': 'عنوان التقرير',
            'details': 'التفاصيل',
            'branch': 'الفرع المعني',
        }
        
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and hasattr(user, 'managed_company'):
             # إذا كان مدير شركة، اسمح له باختيار الفرع
             self.fields['branch'].queryset = user.managed_company.branches.all()
             self.fields['branch'].widget.attrs.pop('style', None) # إظهار الحقل
        else:
             # إذا كان مدير فرع أو غيره، نخفي ونعطل الحقل (سيتم تعيينه في View)
             self.fields['branch'].required = False

from django import forms
from .models import RestaurantCompany, Branch
from django.contrib.auth import get_user_model

User = get_user_model()

class CompanyForm(forms.ModelForm):
    # نستخدم حقل اختيار للمدراء فقط (الذين لديهم صلاحية manager)
    manager = forms.ModelChoiceField(
        queryset=User.objects.filter(role='manager'),
        required=False,
        label="تعيين مدير",
        empty_label="-- اختر مديراً (اختياري) --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = RestaurantCompany
        fields = ['name', 'manager', 'subscription_status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'اسم المطعم/الشركة'}),
            'subscription_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'اسم الشركة',
            'subscription_status': 'اشتراك نشط',
        }

class BranchForm(forms.ModelForm):
    # خيار اختيار مدير موجود
    manager = forms.ModelChoiceField(
        queryset=User.objects.filter(role='branch_manager'),
        required=False,
        label="اختيار مدير موجود",
        empty_label="-- اختر مديراً (اختياري) --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # حقول إنشاء مدير جديد
    create_new_manager = forms.BooleanField(
        required=False, 
        label="أو إنشاء حساب مدير جديد لهذا الفرع",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'createNewManagerCheck'})
    )
    
    new_manager_username = forms.CharField(
        required=False, 
        label="اسم المستخدم للمدير الجديد",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    new_manager_password = forms.CharField(
        required=False, 
        label="كلمة المرور",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '******'})
    )

    class Meta:
        model = Branch
        fields = ['name', 'location', 'manager', 'waste_threshold']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'مثال: فرع الرياض - العليا'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'الرياض، شارع العليا'}),
            'waste_threshold': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'النسبة المئوية %'}),
        }
        labels = {
            'name': 'اسم الفرع',
            'location': 'الموقع',
            'waste_threshold': 'حد الهدر المسموح (%)',
        }

    def clean(self):
        cleaned_data = super().clean()
        create_new = cleaned_data.get('create_new_manager')
        username = cleaned_data.get('new_manager_username')
        password = cleaned_data.get('new_manager_password')

        if create_new:
            if not username or not password:
                raise forms.ValidationError("يرجى إدخال اسم المستخدم وكلمة المرور للمدير الجديد.")
            
            # التأكد من عدم تكرار اسم المستخدم
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError("اسم المستخدم هذا مستخدم بالفعل. يرجى اختيار اسم آخر.")
        
        return cleaned_data

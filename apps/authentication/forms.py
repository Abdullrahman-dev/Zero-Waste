from django import forms
from .models import User

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="كلمة المرور")

    class Meta:
        model = User
        # يجب أن تطابق هذه الحقول أسماء الـ name في ملف HTML
        fields = ['username', 'email', 'password', 'role']

    def save(self, commit=True):
        user = super().save(commit=False)
        # تشفير كلمة المرور قبل الحفظ
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
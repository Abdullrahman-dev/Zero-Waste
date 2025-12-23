from django import forms
from .models import User
from django.contrib.auth.forms import PasswordResetForm
from apps.notifications.models import EmailLog
from django.utils.html import strip_tags

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


class CustomPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        تجاوز دالة إرسال الإيميل لإضافة سجل في قاعدة البيانات
        """
        # استدعاء الدالة الأصلية لإرسال الإيميل
        super().send_mail(
            subject_template_name, email_template_name, context, from_email,
            to_email, html_email_template_name
        )
        
        # إضافة سجل في قاعدة البيانات
        try:
            from django.template.loader import render_to_string
            subject = render_to_string(subject_template_name, context).strip()
            # إزالة المسافات الزائدة
            subject = " ".join(subject.splitlines())
            
            body = render_to_string(email_template_name, context)
            plain_body = strip_tags(body)
            
            EmailLog.objects.create(
                recipient=to_email,
                email_type='password_reset',
                subject=subject,
                body=plain_body,
                is_sent=True
            )
        except Exception as e:
            # حتى لو فشل التسجيل، لا نريد إيقاف العملية
            pass
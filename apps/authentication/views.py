from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import RegisterForm

# ✅ دالة التسجيل (توجه للوجن مع رسالة نجاح)
def register_view(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # إرسال رسالة نجاح تظهر في صفحة اللوجن بعد التحويل
            messages.success(request, "تم إنشاء الحساب بنجاح! يمكنك الآن الدخول.")
            return redirect('login') 
        else:
            messages.error(request, "يرجى تصحيح الأخطاء أدناه.")
    else:
        form = RegisterForm()
    return render(request, 'authentication/register.html', {'form': form})

# ✅ كلاس تسجيل الدخول المطوّر
class UserLoginView(LoginView):
    template_name = 'authentication/login.html'
    
    # في حال فشل الدخول (كلمة مرور خطأ مثلاً)
    def form_invalid(self, form):
        messages.error(self.request, "اسم المستخدم أو كلمة المرور غير صحيحة.")
        return super().form_invalid(form)

    def get_success_url(self):
        user = self.request.user
        # التوجيه حسب الصلاحية
        if user.role == 'manager': # تأكد أنها 'manager' كما عدلناها في الموديل
            return reverse_lazy('core:dashboard')
        
        elif user.role == 'branch_manager':
            return reverse_lazy('inventory:inventory_list')
            
        return reverse_lazy('core:dashboard')

def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    messages.info(request, "تم تسجيل الخروج بنجاح. نراك قريباً! 👋")
    return redirect('login')
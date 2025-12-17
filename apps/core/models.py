from django.db import models
from django.conf import settings

# 1. الشركة (المطعم الرئيسي)
class RestaurantCompany(models.Model):
    name = models.CharField(max_length=255, verbose_name="اسم الشركة/المطعم")
    foodics_token = models.TextField(blank=True, null=True, verbose_name="Foodics Access Token") # غيرناها لـ TextField لأن التوكين طويل
    subscription_status = models.BooleanField(default=True, verbose_name="حالة الاشتراك")
    
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, # أضفنا هذا لتتمكن من إنشاء شركة بدون مدير مؤقتاً
        related_name='managed_company',
        verbose_name="المدير العام"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# 2. الفرع (مكان المخزون الفعلي)
class Branch(models.Model):
    company = models.ForeignKey(
        RestaurantCompany, 
        on_delete=models.CASCADE, 
        related_name='branches',
        verbose_name="الشركة التابعة"
    )
    
    # حل مشكلة زميلك: كل فرع له مدير خاص
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, # يسمح بإنشاء الفرع أولاً ثم تعيين المدير لاحقاً
        related_name='managed_branch',
        verbose_name="مدير الفرع"
    )
    
    name = models.CharField(max_length=255, verbose_name="اسم الفرع")
    location = models.CharField(max_length=255, verbose_name="الموقع")
    
    # إضافة مهمة: معرف الفرع في نظام فودكس للمزامنة
    foodics_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="Foodics Branch ID")
    
    waste_threshold = models.FloatField(
        default=5.0, # وضعنا قيمة افتراضية 5% لتجنب الأخطاء
        help_text="النسبة المئوية المسموح بها للهدر قبل التنبيه",
        verbose_name="حد الهدر (%)"
    )

    created_at = models.DateTimeField(auto_now_add=True) # لمعرفة متى تم افتتاح الفرع

    def __str__(self):
        return f"{self.name} - {self.company.name}"
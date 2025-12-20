from django.db import models
from datetime import date
from apps.core.models import Branch

# 1️⃣ جدول المنتجات الرئيسي (المرجع)
# هنا نعرف المواد مرة واحدة فقط (مثل: طماطم، دجاج، بيبسي)
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('meat', 'لحوم'),
        ('chicken', 'دجاج'),
        ('vegetables', 'خضروات'),
        ('fruits', 'فواكه'),
        ('dairy', 'ألبان وأجبان'),
        ('drinks', 'مشروبات'),
        ('bakery', 'مخبوزات'),
        ('spices', 'بهارات'),
        ('packaging', 'تغليف'),
        ('other', 'أخرى'),
    ]

    UNIT_CHOICES = [
        ('kg', 'كجم'),
        ('g', 'جم'),
        ('liter', 'لتر'),
        ('ml', 'مل'),
        ('pcs', 'حبة'),
        ('box', 'كرتون'),
    ]

    name = models.CharField(max_length=100, verbose_name="اسم المنتج")
    sku = models.CharField(max_length=50, unique=True, verbose_name="رمز SKU")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, blank=True, null=True, verbose_name="التصنيف")
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='kg', verbose_name="وحدة القياس")
    
    # 🆕 ربط المنتج بالشركة (عزل البيانات)
    from apps.core.models import RestaurantCompany
    company = models.ForeignKey(
        RestaurantCompany, 
        on_delete=models.CASCADE, 
        related_name='products',
        verbose_name="الشركة المالكة",
        null=True, blank=True # جعلناها اختيارية مؤقتاً لتجنب مشاكل البيانات القديمة
    )
    
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="سعر التكلفة (للوحدة)")

    def __str__(self):
        return f"{self.name} ({self.sku})"


# 2️⃣ جدول المخزون التفصيلي (الكميات والتواريخ)
# هذا الجدول يربط المنتج بالفرع ويحفظ تفاصيل الدفعات والتواريخ
class StockItem(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_items')
    
    # بيانات من Foodics
    batch_id = models.CharField(max_length=100, verbose_name="رقم التشغيلة/الباتش")
    quantity = models.FloatField(default=0, verbose_name="الكمية الحالية")
    initial_quantity = models.FloatField(default=0, verbose_name="الكمية الأصلية") # عشان نحسب الاستهلاك
    expiry_date = models.DateField(verbose_name="تاريخ الانتهاء")
    
    # بيانات للذكاء الاصطناعي
    sales_velocity = models.FloatField(default=1.0, verbose_name="معدل الاستهلاك اليومي") # كم نستهلك منه يومياً؟
    last_synced = models.DateTimeField(auto_now=True)

    class Meta:
        # يمنع تكرار نفس الباتش لنفس المنتج في نفس الفرع
        unique_together = ('branch', 'product', 'batch_id')
        verbose_name = "عنصر مخزون"
        verbose_name_plural = "عناصر المخزون"

    # --- دوال مساعدة للعرض في الصفحة ---
    @property
    def days_remaining(self):
        """يحسب الأيام المتبقية للصلاحية"""
        delta = self.expiry_date - date.today()
        return delta.days

    @property
    def status_color(self):
        """يحدد لون التنبيه بناءً على الأيام المتبقية"""
        days = self.days_remaining
        if days < 0: return "danger"    # منتهي (أحمر)
        if days <= 3: return "warning"  # وشك الانتهاء (أصفر)
        return "success"                # سليم (أخضر)

    def __str__(self):
        return f"{self.product.name} - {self.branch.name} ({self.batch_id})"
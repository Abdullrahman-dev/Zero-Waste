from django.db import models
from apps.core.models import Branch

class FoodicsData(models.Model):
    branch = models.ForeignKey(
        Branch, 
        on_delete=models.CASCADE, 
        related_name='inventory_items'
    )
    sku = models.CharField(max_length=100)
    batch_id = models.CharField(max_length=100)
    expiry_date = models.DateField()
    stock_level = models.IntegerField()
    sales_velocity = models.FloatField(default=0.0) # سرعة البيع المتوقعة
    
    last_synced = models.DateTimeField(auto_now=True)

    class Meta:
        # لضمان عدم تكرار نفس الـ Batch في نفس الفرع
        unique_together = ('branch', 'sku', 'batch_id') 

    def __str__(self):
        return f"{self.sku} ({self.stock_level})"
    
from django.db import models
from apps.core.models import Branch

# جدول المنتجات (مثل: برجر، طماطم، بيبسي)
class Product(models.Model):
    name = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

# جدول المخزون (يربط المنتج بالفرع والكمية وتاريخ الانتهاء)
class StockItem(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    expiry_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.branch.name}"
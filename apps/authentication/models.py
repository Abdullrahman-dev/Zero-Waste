from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('manager', 'مدير مطعم (مشرف عام)'),
        ('branch_manager', 'مدير فرع'),
    ]
    
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='branch_manager',
        verbose_name="نوع الحساب"
    )

    # حل مشكلة التصادم E304 بإضافة related_name فريد
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups", 
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
    )

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
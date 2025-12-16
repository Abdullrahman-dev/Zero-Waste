from django.db import models
from django.conf import settings

class RestaurantCompany(models.Model):
    name = models.CharField(max_length=255)
    foodics_token = models.CharField(max_length=500, blank=True, null=True)
    subscription_status = models.BooleanField(default=True)
    
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='managed_company'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Branch(models.Model):
    company = models.ForeignKey(
        RestaurantCompany, 
        on_delete=models.CASCADE, 
        related_name='branches'
    )
    manager = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='managed_branch'
    )
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    waste_threshold = models.FloatField(help_text="The allowed waste percentage before alert")

    def __str__(self):
        return f"{self.name} - {self.company.name}"
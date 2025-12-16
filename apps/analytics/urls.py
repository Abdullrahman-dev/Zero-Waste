# apps/analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('generate/<int:branch_id>/', views.generate_waste_report, name='generate_report'),
]
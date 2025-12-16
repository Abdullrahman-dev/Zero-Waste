# apps/core/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard'), # الرابط الرئيسي
]
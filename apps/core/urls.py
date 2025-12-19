# apps/core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_home, name='dashboard'), # الرابط الرئيسي
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
    path('branches/', views.branch_list, name='branch_list'),
]





   

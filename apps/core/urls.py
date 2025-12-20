# apps/core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard_router, name='dashboard'), # الرابط الرئيسي (Router)
    path('company/add/', views.add_company_view, name='add_company'), # رابط إضافة شركة
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
    path('branches/', views.branch_list, name='branch_list'),
    path('branches/add/', views.add_branch_view, name='add_branch'), # رابط إضافة فرع
]





   

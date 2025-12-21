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
    path('integrations/', views.integrations_view, name='integrations'),
    path('impersonate/<int:user_id>/', views.impersonate_user, name='impersonate_user'),
    path('impersonate/stop/', views.stop_impersonation, name='stop_impersonation'),
    path('company/<int:company_id>/toggle-status/', views.toggle_company_status, name='toggle_company_status'),
]





   

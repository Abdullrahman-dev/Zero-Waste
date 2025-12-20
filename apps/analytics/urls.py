from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('generate/<int:branch_id>/', views.generate_waste_report, name='generate_report'),
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('log/', views.log_waste, name='log_waste'),
    path('history/', views.waste_list, name='waste_list'),
]
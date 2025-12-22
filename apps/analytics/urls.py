from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('generate/<int:branch_id>/', views.generate_waste_report, name='generate_report'),
    path('', views.analytics_dashboard, name='analytics_dashboard'),
    path('log/', views.log_waste, name='log_waste'),
    path('history/', views.waste_list, name='waste_list'),
    
    # New Advanced Analytics & AI
    path('api/stats/', views.analytics_stats_api, name='analytics_stats_api'),
    path('api/magic-advice/', views.magic_ai_advice_api, name='magic_ai_advice_api'),
    path('reduction-advice/', views.reduction_suggestions, name='reduction_suggestions'),
]
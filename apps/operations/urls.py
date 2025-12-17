# apps/operations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.requests_list, name='requests_list'),
    path('api/chart-data/', views.chart_data_api, name='chart_data_api'),
    path('create-promo/<int:branch_id>/', views.create_promo_request, name='create_promo'),
    path('review/<int:request_id>/<str:action>/', views.review_request, name='review_request'),
]
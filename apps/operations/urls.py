# apps/operations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.requests_list, name='requests_list'),
    path('create-promo/<int:branch_id>/', views.create_offer_request, name='create_promo'),
    path('review/<int:request_id>/<str:action>/', views.review_request, name='review_request'),
]
# apps/operations/urls.py
from django.urls import path
from . import views

app_name = 'operations'

urlpatterns = [
    path('', views.requests_list, name='requests_list'),
    path('new/', views.create_request_view, name='create_request'),
    # path('create/<int:branch_id>/', views.create_promo_request, name='create_promo'), # لم نعد بحاجة لهذا
    path('review/<int:request_id>/<str:action>/', views.review_request, name='review_request'),
]
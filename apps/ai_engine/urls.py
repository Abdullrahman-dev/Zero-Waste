from django.urls import path
from . import views

app_name = 'ai_engine'

urlpatterns = [
    path('predict/<int:branch_id>/', views.predict_waste_view, name='predict_waste'),
]

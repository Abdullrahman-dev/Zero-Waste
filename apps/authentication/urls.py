from django.urls import path
from .views import register_view, UserLoginView, logout_view

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
]
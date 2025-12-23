from django.urls import path
from django.contrib.auth import views as auth_views
from .views import register_view, UserLoginView, logout_view

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    # path('register/', register_view, name='register'), # Disabled for B2B security
    
    # Password Reset URLs (تم نقلها للمستوى الجذري للمشروع لتوحيد المسارات)
]

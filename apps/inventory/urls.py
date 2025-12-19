from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_list, name='inventory_list'),
    path('product/add/', views.add_product, name='add_product'),
    path('stock/add/', views.add_stock_item, name='add_stock_item'),
    
    # 👇 روابط التعديل والحذف الجديدة (لاحظ وجود <int:pk>)
    path('stock/<int:pk>/edit/', views.edit_stock_item, name='edit_stock_item'),
    path('stock/<int:pk>/delete/', views.delete_stock_item, name='delete_stock_item'),
]
# stock/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_list, name='stock_list'),
    path('<int:pk>/', views.stock_detail, name='stock_detail'),
    path('create/', views.stock_create, name='stock_create'),
    path('<int:pk>/update/', views.stock_update, name='stock_update'),
    path('<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    path('<int:stock_id>/movimiento/', views.nuevo_movimiento, name='nuevo_movimiento'),
    path('sincronizar/', views.sincronizar_desde_activos, name='sincronizar_stock'),
]
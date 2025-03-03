# obsoletos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.obsoleto_list, name='obsoleto_list'),
    path('<int:pk>/', views.obsoleto_detail, name='obsoleto_detail'),
    path('create/', views.obsoleto_create, name='obsoleto_create'),
    path('<int:pk>/update/', views.obsoleto_update, name='obsoleto_update'),
    path('<int:pk>/delete/', views.obsoleto_delete, name='obsoleto_delete'),
    path('sincronizar/', views.sincronizar_desde_activos, name='sincronizar_obsoletos'),
    path('exportar-excel/', views.exportar_excel, name='exportar_obsoletos_excel'),
]
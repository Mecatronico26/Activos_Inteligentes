# criticos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.critico_list, name='critico_list'),
    path('<int:pk>/', views.critico_detail, name='critico_detail'),
    path('create/', views.critico_create, name='critico_create'),
    path('<int:pk>/update/', views.critico_update, name='critico_update'),
    path('<int:pk>/delete/', views.critico_delete, name='critico_delete'),
    path('sincronizar/', views.sincronizar_desde_activos, name='sincronizar_criticos'),
    path('exportar-excel/', views.exportar_excel, name='exportar_criticos_excel'),
]
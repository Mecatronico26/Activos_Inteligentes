# mantenimiento/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Mantenimientos
    path('', views.mantenimiento_list, name='mantenimiento_list'),
    path('<int:pk>/', views.mantenimiento_detail, name='mantenimiento_detail'),
    path('create/', views.mantenimiento_create, name='mantenimiento_create'),
    path('<int:pk>/update/', views.mantenimiento_update, name='mantenimiento_update'),
    path('<int:pk>/delete/', views.mantenimiento_delete, name='mantenimiento_delete'),
    path('<int:pk>/completar/', views.completar_mantenimiento, name='completar_mantenimiento'),
    path('<int:pk>/posponer/', views.posponer_mantenimiento, name='posponer_mantenimiento'),
    path('programar/', views.programar_desde_activos, name='programar_mantenimientos'),
    path('exportar-excel/', views.exportar_excel, name='exportar_mantenimientos_excel'),
    
    # Mantenimiento Predictivo
    path('predictivo/', views.plan_predictivo_list, name='plan_predictivo_list'),
    path('predictivo/<int:pk>/', views.plan_predictivo_detail, name='plan_predictivo_detail'),
    path('predictivo/create/', views.plan_predictivo_create, name='plan_predictivo_create'),
    path('predictivo/<int:pk>/update/', views.plan_predictivo_update, name='plan_predictivo_update'),
    path('predictivo/<int:pk>/delete/', views.plan_predictivo_delete, name='plan_predictivo_delete'),
    path('predictivo/<int:plan_id>/lectura/', views.lectura_predictiva_create, name='lectura_predictiva_create'),
    path('api/predictivo/<int:plan_id>/datos/', views.obtener_datos_predictivos, name='obtener_datos_predictivos'),
]
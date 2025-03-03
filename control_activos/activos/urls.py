# activos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.activo_list, name='activo_list'),
    path('<int:pk>/', views.activo_detail, name='activo_detail'),
    path('create/', views.activo_create, name='activo_create'),
    path('<int:pk>/update/', views.activo_update, name='activo_update'),
    path('<int:pk>/delete/', views.activo_delete, name='activo_delete'),
    path('upload-excel/', views.upload_excel, name='upload_excel'),
    path('api/get-subareas/', views.get_subareas, name='get_subareas'),
]
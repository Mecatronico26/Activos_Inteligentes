# ai_urls.py
from django.urls import path
from . import ai_views

urlpatterns = [
    path('dashboard/', ai_views.dashboard_ia, name='dashboard_ia'),
    path('criticidad/', ai_views.analisis_criticidad, name='analisis_criticidad'),
    path('prediccion-fallas/', ai_views.prediccion_fallas, name='prediccion_fallas'),
    path('optimizacion-mantenimiento/', ai_views.optimizacion_mantenimiento, name='optimizacion_mantenimiento'),
    path('deteccion-anomalias/', ai_views.deteccion_anomalias, name='deteccion_anomalias'),
    path('aplicar-recomendaciones/', ai_views.aplicar_recomendaciones, name='aplicar_recomendaciones'),
]
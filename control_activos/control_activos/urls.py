# control_activos/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from activos.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('activos/', include('activos.urls')),
    path('stock/', include('stock.urls')),
    path('criticos/', include('criticos.urls')),
    path('obsoletos/', include('obsoletos.urls')),
    path('mantenimiento/', include('mantenimiento.urls')),
]

# Añadir URLs para archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
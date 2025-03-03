# activos/models.py
from django.db import models

class Area(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"
        ordering = ['nombre']

class SubArea(models.Model):
    nombre = models.CharField(max_length=100)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='subareas')
    descripcion = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} ({self.area.nombre})"
    
    class Meta:
        verbose_name = "Subárea"
        verbose_name_plural = "Subáreas"
        ordering = ['area__nombre', 'nombre']
        unique_together = ['nombre', 'area']

class Fabricante(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    pais = models.CharField(max_length=100, blank=True, null=True)
    sitio_web = models.URLField(blank=True, null=True)
    correo_contacto = models.EmailField(blank=True, null=True)
    telefono_contacto = models.CharField(max_length=50, blank=True, null=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Fabricante"
        verbose_name_plural = "Fabricantes"
        ordering = ['nombre']

class Activo(models.Model):
    nombre = models.CharField(max_length=200)
    modelo = models.CharField(max_length=100)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.CASCADE, related_name='activos')
    version = models.CharField(max_length=50, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='activos')
    subarea = models.ForeignKey(SubArea, on_delete=models.CASCADE, related_name='activos')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    imagen = models.ImageField(upload_to='activos/', blank=True, null=True)
    codigo_interno = models.CharField(max_length=50, blank=True, null=True)
    numero_serie = models.CharField(max_length=100, blank=True, null=True)
    fecha_adquisicion = models.DateField(blank=True, null=True)
    precio_adquisicion = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.modelo} ({self.fabricante})"
    
    class Meta:
        verbose_name = "Activo"
        verbose_name_plural = "Activos"
        ordering = ['area__nombre', 'subarea__nombre', 'nombre']
# obsoletos/models.py
from django.db import models
from django.utils import timezone
from activos.models import Fabricante

class ActivoObsoleto(models.Model):
    ESTADO_CHOICES = [
        ('funcional', 'Funcional'),
        ('deteriorado', 'Deteriorado'),
        ('obsoleto', 'Tecnológicamente Obsoleto'),
        ('falla', 'Con Fallas Recurrentes'),
        ('discontinuado', 'Discontinuado por Fabricante'),
    ]
    
    DISPONIBILIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
        ('nula', 'Nula'),
        ('descontinuada', 'Descontinuada por Fabricante'),
    ]
    
    ESTRATEGIA_CHOICES = [
        ('reemplazo', 'Reemplazo Total'),
        ('actualización', 'Actualización'),
        ('extensión', 'Extensión de Vida Útil'),
        ('redesign', 'Rediseño del Sistema'),
        ('redundancia', 'Implementar Redundancia'),
        ('outsourcing', 'Outsourcing del Servicio'),
        ('otra', 'Otra Estrategia'),
    ]
    
    IMPACTO_CHOICES = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
        ('critico', 'Crítico'),
    ]
    
    nombre = models.CharField(max_length=200)
    modelo = models.CharField(max_length=100, unique=True)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.CASCADE, related_name='activos_obsoletos')
    ano_instalacion = models.PositiveIntegerField(verbose_name='Año Instalación')
    vida_util = models.PositiveIntegerField(verbose_name='Vida Útil (años)')
    estado_actual = models.CharField(max_length=20, choices=ESTADO_CHOICES)
    disponibilidad_repuestos = models.CharField(max_length=20, choices=DISPONIBILIDAD_CHOICES)
    estrategia_mitigacion = models.CharField(max_length=20, choices=ESTRATEGIA_CHOICES)
    fecha_renovacion = models.DateField(blank=True, null=True)
    presupuesto_estimado = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    impacto_produccion = models.CharField(max_length=20, choices=IMPACTO_CHOICES)
    observaciones = models.TextField(blank=True, null=True)
    fecha_evaluacion = models.DateField(auto_now_add=True)
    responsable_evaluacion = models.CharField(max_length=100, blank=True, null=True)
    
    def anos_en_servicio(self):
        """Calcula años en servicio desde la instalación"""
        return timezone.now().year - self.ano_instalacion
    
    def porcentaje_vida_util_consumida(self):
        """Calcula el porcentaje de vida útil consumida"""
        anos_servicio = self.anos_en_servicio()
        if anos_servicio >= self.vida_util:
            return 100
        return round((anos_servicio / self.vida_util) * 100, 1)
    
    def dias_hasta_renovacion(self):
        """Calcula días restantes hasta la fecha de renovación prevista"""
        if not self.fecha_renovacion:
            return None
        delta = self.fecha_renovacion - timezone.now().date()
        return delta.days
    
    def __str__(self):
        return f"{self.nombre} - {self.modelo} ({self.fabricante}) - Estado: {self.get_estado_actual_display()}"
    
    class Meta:
        verbose_name = "Activo Obsoleto"
        verbose_name_plural = "Activos Obsoletos"
        ordering = ['nombre', 'modelo']
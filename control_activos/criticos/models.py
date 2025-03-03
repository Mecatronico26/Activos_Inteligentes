# criticos/models.py
from django.db import models
from activos.models import Fabricante

class ActivoCritico(models.Model):
    IMPACTO_CHOICES = [
        ('bajo', 'Bajo'),
        ('medio', 'Medio'),
        ('alto', 'Alto'),
        ('critico', 'Crítico'),
    ]
    
    DISPONIBILIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
        ('nula', 'Nula'),
    ]
    
    PROBABILIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]
    
    CRITICIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('extrema', 'Extrema'),
    ]
    
    ESTRATEGIA_CHOICES = [
        ('reemplazo', 'Reemplazo Planificado'),
        ('stock', 'Mantener Stock'),
        ('monitoreo', 'Monitoreo Continuo'),
        ('mantenimiento', 'Mantenimiento Preventivo'),
        ('redundancia', 'Implementar Redundancia'),
        ('otro', 'Otra Estrategia'),
    ]
    
    nombre = models.CharField(max_length=200)
    modelo = models.CharField(max_length=100, unique=True)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.CASCADE, related_name='activos_criticos')
    impacto_produccion = models.CharField(max_length=20, choices=IMPACTO_CHOICES)
    disponibilidad_repuestos = models.CharField(max_length=20, choices=DISPONIBILIDAD_CHOICES)
    probabilidad_falla = models.CharField(max_length=20, choices=PROBABILIDAD_CHOICES)
    criticidad = models.CharField(max_length=20, choices=CRITICIDAD_CHOICES)
    estrategia_recomendada = models.CharField(max_length=50, choices=ESTRATEGIA_CHOICES)
    observaciones = models.TextField(blank=True, null=True)
    fecha_evaluacion = models.DateField(auto_now_add=True)
    fecha_revision = models.DateField(blank=True, null=True)
    responsable_evaluacion = models.CharField(max_length=100, blank=True, null=True)
    
    def calcular_criticidad(self):
        """
        Método para calcular automáticamente la criticidad basada en otros parámetros
        """
        # Mapeo de valores a números para el cálculo
        impacto_map = {'bajo': 1, 'medio': 2, 'alto': 3, 'critico': 4}
        disponibilidad_map = {'alta': 1, 'media': 2, 'baja': 3, 'nula': 4}
        probabilidad_map = {'baja': 1, 'media': 2, 'alta': 3}
        
        # Cálculo ponderado
        impacto_valor = impacto_map.get(self.impacto_produccion, 1)
        disponibilidad_valor = disponibilidad_map.get(self.disponibilidad_repuestos, 1)
        probabilidad_valor = probabilidad_map.get(self.probabilidad_falla, 1)
        
        # Fórmula: Impacto * Probabilidad * Factor de disponibilidad
        valor_criticidad = impacto_valor * probabilidad_valor * (disponibilidad_valor / 2)
        
        # Asignación de categoría
        if valor_criticidad <= 2:
            return 'baja'
        elif valor_criticidad <= 5:
            return 'media'
        elif valor_criticidad <= 9:
            return 'alta'
        else:
            return 'extrema'
    
    def save(self, *args, **kwargs):
        # Calcular la criticidad antes de guardar si no se ha establecido manualmente
        if not self.criticidad or self.criticidad == '':
            self.criticidad = self.calcular_criticidad()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombre} - {self.modelo} ({self.fabricante}) - Criticidad: {self.get_criticidad_display()}"
    
    class Meta:
        verbose_name = "Activo Crítico"
        verbose_name_plural = "Activos Críticos"
        ordering = ['-criticidad', 'nombre']
# mantenimiento/models.py
from django.db import models
from activos.models import Activo, Fabricante
from django.utils import timezone

class Mantenimiento(models.Model):
    TIPO_CHOICES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
        ('predictivo', 'Predictivo'),
    ]
    
    ESTADO_CHOICES = [
        ('programado', 'Programado'),
        ('en_proceso', 'En Proceso'),
        ('completado', 'Completado'),
        ('pospuesto', 'Pospuesto'),
        ('cancelado', 'Cancelado'),
    ]
    
    nombre = models.CharField(max_length=200)
    modelo = models.CharField(max_length=100)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.CASCADE, related_name='mantenimientos')
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name='mantenimientos', blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    fecha_programada = models.DateField()
    fecha_realizada = models.DateField(blank=True, null=True)
    responsable = models.CharField(max_length=100)
    acciones = models.TextField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='programado')
    duracion_estimada = models.PositiveIntegerField(help_text='Duración estimada en minutos', blank=True, null=True)
    duracion_real = models.PositiveIntegerField(help_text='Duración real en minutos', blank=True, null=True)
    costo_estimado = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    costo_real = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    requiere_parada = models.BooleanField(default=False)
    requiere_repuestos = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    def esta_atrasado(self):
        """Verifica si el mantenimiento está atrasado"""

        if self.estado == 'programado' and self.fecha_programada < timezone.now().date():
            return True
        return False
    
    def eficiencia_tiempo(self):
        """Calcula la eficiencia en tiempo si ambos datos están disponibles"""
        if self.duracion_estimada and self.duracion_real:
            return round((self.duracion_estimada / self.duracion_real) * 100, 1)
        return None
    
    def eficiencia_costo(self):
        """Calcula la eficiencia en costos si ambos datos están disponibles"""
        if self.costo_estimado and self.costo_real:
            return round((self.costo_estimado / self.costo_real) * 100, 1)
        return None
    
    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre} ({self.modelo}) - {self.fecha_programada}"
    
    class Meta:
        verbose_name = "Mantenimiento"
        verbose_name_plural = "Mantenimientos"
        ordering = ['fecha_programada', 'tipo']
        
class PlanMantenimientoPredictivo(models.Model):
    FRECUENCIA_CHOICES = [
        ('diaria', 'Diaria'),
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('semestral', 'Semestral'),
        ('anual', 'Anual'),
    ]
    
    activo = models.ForeignKey(Activo, on_delete=models.CASCADE, related_name='planes_predictivos')
    nombre_plan = models.CharField(max_length=200)
    descripcion = models.TextField()
    parametros_medicion = models.CharField(max_length=200, help_text='Parámetros que se medirán (temperatura, vibración, etc.)')
    valor_umbral = models.FloatField(help_text='Valor umbral para generar alerta')
    unidad_medida = models.CharField(max_length=50)
    frecuencia_medicion = models.CharField(max_length=20, choices=FRECUENCIA_CHOICES)
    responsable = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    activo = models.BooleanField(default=True)
    observaciones = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Plan Predictivo: {self.nombre_plan} para {self.activo}"
    
    class Meta:
        verbose_name = "Plan de Mantenimiento Predictivo"
        verbose_name_plural = "Planes de Mantenimiento Predictivo"
        ordering = ['activo', 'nombre_plan']

class LecturaPredictiva(models.Model):
    plan = models.ForeignKey(PlanMantenimientoPredictivo, on_delete=models.CASCADE, related_name='lecturas')
    valor_medido = models.FloatField()
    fecha_lectura = models.DateTimeField()
    responsable = models.CharField(max_length=100)
    observaciones = models.TextField(blank=True, null=True)
    supera_umbral = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Verificar si supera el umbral
        if self.valor_medido > self.plan.valor_umbral:
            self.supera_umbral = True
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Lectura de {self.plan.nombre_plan}: {self.valor_medido} {self.plan.unidad_medida} ({self.fecha_lectura})"
    
    class Meta:
        verbose_name = "Lectura Predictiva"
        verbose_name_plural = "Lecturas Predictivas"
        ordering = ['-fecha_lectura']
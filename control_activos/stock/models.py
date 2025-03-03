# stock/models.py
from django.db import models
from activos.models import Fabricante

class StockActivo(models.Model):
    nombre = models.CharField(max_length=200)
    modelo = models.CharField(max_length=100, unique=True)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.CASCADE, related_name='stock_activos')
    cantidad = models.PositiveIntegerField(default=0)
    cantidad_minima = models.PositiveIntegerField(default=1)
    ubicacion_almacen = models.CharField(max_length=100, blank=True, null=True)
    fecha_ultima_actualizacion = models.DateTimeField(auto_now=True)
    notas = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.modelo} ({self.fabricante}) - Stock: {self.cantidad}"
    
    def estado_stock(self):
        if self.cantidad <= 0:
            return "Sin stock"
        elif self.cantidad < self.cantidad_minima:
            return "Stock bajo"
        else:
            return "Stock adecuado"
    
    class Meta:
        verbose_name = "Stock Activo"
        verbose_name_plural = "Stock Activos"
        ordering = ['nombre', 'modelo']

class MovimientoStock(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste de inventario'),
    ]
    
    stock_activo = models.ForeignKey(StockActivo, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    responsable = models.CharField(max_length=100)
    destino = models.CharField(max_length=200, blank=True, null=True)
    orden_trabajo = models.CharField(max_length=50, blank=True, null=True)
    comentarios = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.get_tipo_display()} de {self.cantidad} unidades de {self.stock_activo.nombre}"
    
    class Meta:
        verbose_name = "Movimiento de Stock"
        verbose_name_plural = "Movimientos de Stock"
        ordering = ['-fecha']
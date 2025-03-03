# stock/forms.py
from django import forms
from .models import StockActivo, MovimientoStock

class StockActivoForm(forms.ModelForm):
    class Meta:
        model = StockActivo
        fields = [
            'nombre', 'modelo', 'fabricante', 'cantidad', 'cantidad_minima', 
            'ubicacion_almacen', 'notas'
        ]
        widgets = {
            'notas': forms.Textarea(attrs={'rows': 3}),
        }

class MovimientoStockForm(forms.ModelForm):
    class Meta:
        model = MovimientoStock
        fields = ['tipo', 'cantidad', 'responsable', 'destino', 'orden_trabajo', 'comentarios']
        widgets = {
            'comentarios': forms.Textarea(attrs={'rows': 3}),
            'responsable': forms.TextInput(attrs={'placeholder': 'Nombre del responsable'}),
            'destino': forms.TextInput(attrs={'placeholder': 'Destino (para salidas)'}),
            'orden_trabajo': forms.TextInput(attrs={'placeholder': 'Número de orden de trabajo (opcional)'}),
        }
    
    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise forms.ValidationError('La cantidad debe ser mayor que cero')
        return cantidad
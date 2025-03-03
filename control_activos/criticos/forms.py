# criticos/forms.py
from django import forms
from .models import ActivoCritico
from django.utils import timezone

class ActivoCriticoForm(forms.ModelForm):
    class Meta:
        model = ActivoCritico
        fields = [
            'nombre', 'modelo', 'fabricante', 'impacto_produccion', 
            'disponibilidad_repuestos', 'probabilidad_falla', 'criticidad', 
            'estrategia_recomendada', 'observaciones', 'responsable_evaluacion',
            'fecha_revision'
        ]
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'fecha_revision': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar fecha de revisión predeterminada a 1 año desde hoy
        if not self.instance.pk:  # Solo para nuevos registros
            self.fields['fecha_revision'].initial = timezone.now().date().replace(year=timezone.now().year + 1)
        
        # Añadir clases y descripciones para mejor UI
        self.fields['impacto_produccion'].help_text = 'Nivel de impacto que tendría en la producción un fallo de este activo'
        self.fields['disponibilidad_repuestos'].help_text = 'Disponibilidad de repuestos en el mercado'
        self.fields['probabilidad_falla'].help_text = 'Probabilidad de ocurrencia de fallas'
        
    def clean(self):
        cleaned_data = super().clean()
        
        # Opcionalmente, calcular criticidad automáticamente basado en otros campos
        calcular_auto = self.data.get('calcular_criticidad_auto', False) == 'on'
        if calcular_auto:
            # Mapeo de valores a números para el cálculo
            impacto = cleaned_data.get('impacto_produccion')
            disponibilidad = cleaned_data.get('disponibilidad_repuestos')
            probabilidad = cleaned_data.get('probabilidad_falla')
            
            if impacto and disponibilidad and probabilidad:
                # Usar el método de la clase modelo para calcular
                instance = ActivoCritico(
                    impacto_produccion=impacto,
                    disponibilidad_repuestos=disponibilidad,
                    probabilidad_falla=probabilidad
                )
                cleaned_data['criticidad'] = instance.calcular_criticidad()
        
        return cleaned_data
# obsoletos/forms.py
from django import forms
from .models import ActivoObsoleto
from django.utils import timezone
from datetime import timedelta

class ActivoObsoletoForm(forms.ModelForm):
    class Meta:
        model = ActivoObsoleto
        fields = [
            'nombre', 'modelo', 'fabricante', 'ano_instalacion', 'vida_util',
            'estado_actual', 'disponibilidad_repuestos', 'estrategia_mitigacion',
            'fecha_renovacion', 'presupuesto_estimado', 'impacto_produccion',
            'observaciones', 'responsable_evaluacion'
        ]
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'fecha_renovacion': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar fecha de renovación predeterminada a 6 meses desde hoy
        if not self.instance.pk:  # Solo para nuevos registros
            self.fields['fecha_renovacion'].initial = timezone.now().date() + timedelta(days=180)
            self.fields['ano_instalacion'].initial = timezone.now().year - 5  # Valor predeterminado de 5 años
            self.fields['vida_util'].initial = 10  # Valor predeterminado de 10 años
        
        # Añadir clases y descripciones para mejor UI
        self.fields['ano_instalacion'].help_text = 'Año en que fue instalado o adquirido el activo'
        self.fields['vida_util'].help_text = 'Vida útil estimada en años'
        self.fields['fecha_renovacion'].help_text = 'Fecha estimada para renovación o reemplazo'
        self.fields['presupuesto_estimado'].help_text = 'Presupuesto estimado para reemplazo o renovación'
        
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar que el año de instalación no sea mayor al actual
        ano_instalacion = cleaned_data.get('ano_instalacion')
        if ano_instalacion and ano_instalacion > timezone.now().year:
            self.add_error('ano_instalacion', 'El año de instalación no puede ser mayor al año actual')
        
        # Validar que la fecha de renovación no sea anterior a hoy
        fecha_renovacion = cleaned_data.get('fecha_renovacion')
        if fecha_renovacion and fecha_renovacion < timezone.now().date():
            self.add_error('fecha_renovacion', 'La fecha de renovación no puede ser anterior a hoy')
        
        return cleaned_data
# mantenimiento/forms.py
from django import forms
from .models import Mantenimiento, PlanMantenimientoPredictivo, LecturaPredictiva
from django.utils import timezone

class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = Mantenimiento
        fields = [
            'nombre', 'modelo', 'fabricante', 'activo', 'tipo', 
            'fecha_programada', 'responsable', 'acciones', 'estado',
            'duracion_estimada', 'costo_estimado', 'requiere_parada',
            'requiere_repuestos', 'observaciones'
        ]
        widgets = {
            'fecha_programada': forms.DateInput(attrs={'type': 'date'}),
            'acciones': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar fecha programada predeterminada a 1 semana desde hoy para nuevos registros
        if not self.instance.pk:
            self.fields['fecha_programada'].initial = timezone.now().date() + timezone.timedelta(days=7)
            self.fields['estado'].initial = 'programado'
        
        # Añadir clases y descripciones para mejor UI
        self.fields['duracion_estimada'].help_text = 'Duración estimada en minutos'
        self.fields['costo_estimado'].help_text = 'Costo estimado del mantenimiento'
        self.fields['requiere_parada'].help_text = 'Requiere parada de equipos/sistemas'
        self.fields['requiere_repuestos'].help_text = 'Requiere uso de repuestos del stock'

class PlanMantenimientoPreditivoForm(forms.ModelForm):
    class Meta:
        model = PlanMantenimientoPredictivo
        fields = [
            'activo', 'nombre_plan', 'descripcion', 'parametros_medicion',
            'valor_umbral', 'unidad_medida', 'frecuencia_medicion',
            'responsable', 'fecha_inicio', 'activo', 'observaciones'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar fecha inicio predeterminada a hoy para nuevos registros
        if not self.instance.pk:
            self.fields['fecha_inicio'].initial = timezone.now().date()
            self.fields['activo'].initial = True
        
        # Añadir clases y descripciones para mejor UI
        self.fields['parametros_medicion'].help_text = 'Parámetros que se medirán (temperatura, vibración, etc.)'
        self.fields['valor_umbral'].help_text = 'Valor umbral para generar alerta'
        self.fields['unidad_medida'].help_text = 'Unidad de medida (°C, mm/s, etc.)'

class LecturaPreditivaForm(forms.ModelForm):
    crear_mantenimiento = forms.BooleanField(
        required=False, 
        label='Crear mantenimiento correctivo si supera umbral',
        help_text='Si se activa, y la lectura supera el umbral, se creará automáticamente un mantenimiento correctivo',
        initial=True
    )
    
    class Meta:
        model = LecturaPredictiva
        fields = ['valor_medido', 'responsable', 'observaciones']
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Valores predeterminados
        self.fields['fecha_lectura'] = forms.DateTimeField(
            initial=timezone.now(),
            widget=forms.DateTimeInput(attrs={'type': 'datetime-local'})
        )
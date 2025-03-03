# activos/forms.py
from django import forms
from .models import Activo, Area, SubArea, Fabricante

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nombre', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class SubAreaForm(forms.ModelForm):
    class Meta:
        model = SubArea
        fields = ['nombre', 'area', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }

class FabricanteForm(forms.ModelForm):
    class Meta:
        model = Fabricante
        fields = ['nombre', 'pais', 'sitio_web', 'correo_contacto', 'telefono_contacto']

class ActivoForm(forms.ModelForm):
    class Meta:
        model = Activo
        fields = [
            'nombre', 'modelo', 'fabricante', 'version', 'descripcion', 
            'area', 'subarea', 'imagen', 'codigo_interno', 'numero_serie',
            'fecha_adquisicion', 'precio_adquisicion'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
            'fecha_adquisicion': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si hay una instancia existente, filtrar subáreas
        if 'instance' in kwargs and kwargs['instance']:
            activo = kwargs['instance']
            if activo.area:
                self.fields['subarea'].queryset = SubArea.objects.filter(area=activo.area)
        else:
            # Si es un formulario nuevo, inicialmente no mostrar subáreas
            self.fields['subarea'].queryset = SubArea.objects.none()
        
        # Añadir clases para estilos y JavaScript
        self.fields['area'].widget.attrs.update({'class': 'form-control', 'id': 'id_area_select'})
        self.fields['subarea'].widget.attrs.update({'class': 'form-control', 'id': 'id_subarea_select'})

class UploadExcelForm(forms.Form):
    excel_file = forms.FileField(
        label='Archivo Excel',
        help_text='Seleccione un archivo Excel (.xlsx, .xls) con los activos a importar'
    )
    
    def clean_excel_file(self):
        file = self.cleaned_data.get('excel_file')
        if file:
            # Verificar extensión
            extension = file.name.split('.')[-1].lower()
            if extension not in ['xlsx', 'xls']:
                raise forms.ValidationError(
                    'El archivo debe ser un Excel válido (.xlsx, .xls)'
                )
        return file
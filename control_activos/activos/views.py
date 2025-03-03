# activos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
import pandas as pd
import io
from .models import Activo, Area, SubArea, Fabricante
from .forms import ActivoForm, AreaForm, SubAreaForm, FabricanteForm, UploadExcelForm
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

def home(request):
    """Vista de la página principal con botones de navegación"""
    return render(request, 'home.html')

def activo_list(request):
    """Lista de activos con filtrado"""
    activos = Activo.objects.all()
    
    # Filtrado por parámetros
    modelo = request.GET.get('modelo', '')
    fabricante = request.GET.get('fabricante', '')
    area = request.GET.get('area', '')
    subarea = request.GET.get('subarea', '')
    
    if modelo:
        activos = activos.filter(modelo__icontains=modelo)
    if fabricante:
        activos = activos.filter(fabricante__nombre__icontains=fabricante)
    if area:
        activos = activos.filter(area__nombre__icontains=area)
    if subarea:
        activos = activos.filter(subarea__nombre__icontains=subarea)
    
    # Para formularios de filtrado
    areas = Area.objects.all()
    fabricantes = Fabricante.objects.all()
    
    context = {
        'activos': activos,
        'areas': areas, 
        'fabricantes': fabricantes,
        'modelo_filter': modelo,
        'fabricante_filter': fabricante,
        'area_filter': area,
        'subarea_filter': subarea,
    }
    
    return render(request, 'activos/activo_list.html', context)

def activo_detail(request, pk):
    """Detalle de un activo específico"""
    activo = get_object_or_404(Activo, pk=pk)
    return render(request, 'activos/activo_detail.html', {'activo': activo})

def activo_create(request):
    """Crear un nuevo activo"""
    if request.method == 'POST':
        form = ActivoForm(request.POST, request.FILES)
        if form.is_valid():
            activo = form.save()
            messages.success(request, f'Activo {activo.nombre} creado correctamente.')
            return redirect('activo_detail', pk=activo.pk)
    else:
        form = ActivoForm()
    
    return render(request, 'activos/activo_form.html', {'form': form, 'title': 'Nuevo Activo'})

def activo_update(request, pk):
    """Actualizar un activo existente"""
    activo = get_object_or_404(Activo, pk=pk)
    
    if request.method == 'POST':
        form = ActivoForm(request.POST, request.FILES, instance=activo)
        if form.is_valid():
            activo = form.save()
            messages.success(request, f'Activo {activo.nombre} actualizado correctamente.')
            return redirect('activo_detail', pk=activo.pk)
    else:
        form = ActivoForm(instance=activo)
    
    return render(request, 'activos/activo_form.html', {
        'form': form, 
        'activo': activo,
        'title': 'Editar Activo'
    })

def activo_delete(request, pk):
    """Eliminar un activo"""
    activo = get_object_or_404(Activo, pk=pk)
    
    if request.method == 'POST':
        nombre = activo.nombre
        activo.delete()
        messages.success(request, f'Activo {nombre} eliminado correctamente.')
        return redirect('activo_list')
    
    return render(request, 'activos/activo_confirm_delete.html', {'activo': activo})

def upload_excel(request):
    """Carga masiva de activos desde archivo Excel"""
    if request.method == 'POST':
        form = UploadExcelForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            
            # Leer el archivo con pandas
            try:
                df = pd.read_excel(excel_file)
                
                # Verificar columnas requeridas
                required_columns = ['nombre', 'modelo', 'fabricante', 'area', 'subarea']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    messages.error(request, f'Faltan columnas requeridas: {", ".join(missing_columns)}')
                    return redirect('upload_excel')
                
                # Contador de activos importados y errores
                imported_count = 0
                errors = []
                
                # Procesar cada fila
                for index, row in df.iterrows():
                    try:
                        # Buscar o crear fabricante
                        fabricante, _ = Fabricante.objects.get_or_create(
                            nombre=row['fabricante']
                        )
                        
                        # Buscar o crear área
                        area, _ = Area.objects.get_or_create(
                            nombre=row['area']
                        )
                        
                        # Buscar o crear subárea
                        subarea, _ = SubArea.objects.get_or_create(
                            nombre=row['subarea'],
                            area=area
                        )
                        
                        # Crear el activo
                        activo = Activo(
                            nombre=row['nombre'],
                            modelo=row['modelo'],
                            fabricante=fabricante,
                            area=area,
                            subarea=subarea
                        )
                        
                        # Campos opcionales
                        if 'version' in df.columns and not pd.isna(row['version']):
                            activo.version = row['version']
                        
                        if 'descripcion' in df.columns and not pd.isna(row['descripcion']):
                            activo.descripcion = row['descripcion']
                            
                        activo.save()
                        imported_count += 1
                        
                    except Exception as e:
                        errors.append(f"Error en fila {index+2}: {str(e)}")
                
                # Mostrar resultado
                if imported_count > 0:
                    messages.success(request, f'Se importaron {imported_count} activos correctamente.')
                
                if errors:
                    for error in errors[:10]:  # Mostrar hasta 10 errores
                        messages.warning(request, error)
                    
                    if len(errors) > 10:
                        messages.warning(request, f'... y {len(errors) - 10} errores más.')
                
                return redirect('activo_list')
                
            except Exception as e:
                messages.error(request, f'Error al procesar el archivo: {str(e)}')
                return redirect('upload_excel')
    else:
        form = UploadExcelForm()
    
    return render(request, 'activos/upload_excel.html', {'form': form})

def get_subareas(request):
    """API para obtener subáreas de un área específica (para formularios dinámicos)"""
    area_id = request.GET.get('area_id')
    subareas = SubArea.objects.filter(area_id=area_id).values('id', 'nombre')
    return JsonResponse(list(subareas), safe=False)
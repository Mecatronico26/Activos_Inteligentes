# criticos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from activos.models import Activo, Fabricante
from .models import ActivoCritico
from .forms import ActivoCriticoForm
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from datetime import datetime

def critico_list(request):
    """Lista de activos críticos"""
    activos_criticos = ActivoCritico.objects.all()
    
    # Filtrado
    query = request.GET.get('q', '')
    criticidad = request.GET.get('criticidad', '')
    impacto = request.GET.get('impacto', '')
    
    if query:
        activos_criticos = activos_criticos.filter(
            Q(nombre__icontains=query) | 
            Q(modelo__icontains=query) |
            Q(fabricante__nombre__icontains=query)
        )
    
    if criticidad:
        activos_criticos = activos_criticos.filter(criticidad=criticidad)
        
    if impacto:
        activos_criticos = activos_criticos.filter(impacto_produccion=impacto)
    
    # Resumen por criticidad
    resumen_criticidad = (
        ActivoCritico.objects
        .values('criticidad')
        .annotate(count=Count('id'))
        .order_by('criticidad')
    )
    
    context = {
        'activos_criticos': activos_criticos,
        'query': query,
        'criticidad_filter': criticidad,
        'impacto_filter': impacto,
        'resumen_criticidad': resumen_criticidad,
        'criticidad_choices': ActivoCritico.CRITICIDAD_CHOICES,
        'impacto_choices': ActivoCritico.IMPACTO_CHOICES,
    }
    
    return render(request, 'criticos/critico_list.html', context)

def critico_detail(request, pk):
    """Detalle de un activo crítico"""
    activo_critico = get_object_or_404(ActivoCritico, pk=pk)
    return render(request, 'criticos/critico_detail.html', {'activo_critico': activo_critico})

def critico_create(request):
    """Crear un nuevo activo crítico"""
    if request.method == 'POST':
        form = ActivoCriticoForm(request.POST)
        if form.is_valid():
            activo_critico = form.save()
            messages.success(request, f'Activo crítico {activo_critico.nombre} creado correctamente.')
            return redirect('critico_detail', pk=activo_critico.pk)
    else:
        form = ActivoCriticoForm()
    
    return render(request, 'criticos/critico_form.html', {'form': form, 'title': 'Nuevo Activo Crítico'})

def critico_update(request, pk):
    """Actualizar un activo crítico existente"""
    activo_critico = get_object_or_404(ActivoCritico, pk=pk)
    
    if request.method == 'POST':
        form = ActivoCriticoForm(request.POST, instance=activo_critico)
        if form.is_valid():
            activo_critico = form.save()
            messages.success(request, f'Activo crítico {activo_critico.nombre} actualizado correctamente.')
            return redirect('critico_detail', pk=activo_critico.pk)
    else:
        form = ActivoCriticoForm(instance=activo_critico)
    
    return render(request, 'criticos/critico_form.html', {
        'form': form, 
        'activo_critico': activo_critico,
        'title': 'Editar Activo Crítico'
    })

def critico_delete(request, pk):
    """Eliminar un activo crítico"""
    activo_critico = get_object_or_404(ActivoCritico, pk=pk)
    
    if request.method == 'POST':
        nombre = activo_critico.nombre
        activo_critico.delete()
        messages.success(request, f'Activo crítico {nombre} eliminado correctamente.')
        return redirect('critico_list')
    
    return render(request, 'criticos/critico_confirm_delete.html', {'activo_critico': activo_critico})

def sincronizar_desde_activos(request):
    """Sincronizar activos críticos desde los activos registrados"""
    if request.method == 'POST':
        # Obtener activos agrupados por modelo/fabricante
        activos_agrupados = (
            Activo.objects
            .values('modelo', 'fabricante__id', 'fabricante__nombre', 'nombre')
            .annotate(count=Count('id'))
            .order_by('modelo')
        )
        
        nuevos = 0
        existentes = 0
        
        for grupo in activos_agrupados:
            fabricante = Fabricante.objects.get(id=grupo['fabricante__id'])
            
            # Verificar si ya existe en críticos
            critico_existente = ActivoCritico.objects.filter(
                modelo=grupo['modelo'],
                fabricante=fabricante
            ).first()
            
            if not critico_existente:
                # Crear nuevo registro de activo crítico con valores predeterminados
                ActivoCritico.objects.create(
                    nombre=grupo['nombre'],
                    modelo=grupo['modelo'],
                    fabricante=fabricante,
                    impacto_produccion='medio',
                    disponibilidad_repuestos='media',
                    probabilidad_falla='media',
                    estrategia_recomendada='mantenimiento',
                    observaciones='Creado automáticamente desde sincronización de activos'
                )
                nuevos += 1
            else:
                existentes += 1
        
        messages.success(
            request, 
            f'Sincronización completada. {nuevos} nuevos activos críticos creados. {existentes} ya existían.'
        )
        return redirect('critico_list')
    
    return render(request, 'criticos/sincronizar_confirm.html')

def exportar_excel(request):
    """Exportar activos críticos a Excel"""
    # Obtener datos filtrados si hay parámetros
    activos_criticos = ActivoCritico.objects.all()
    query = request.GET.get('q', '')
    criticidad = request.GET.get('criticidad', '')
    impacto = request.GET.get('impacto', '')
    
    if query:
        activos_criticos = activos_criticos.filter(
            Q(nombre__icontains=query) | 
            Q(modelo__icontains=query) |
            Q(fabricante__nombre__icontains=query)
        )
    
    if criticidad:
        activos_criticos = activos_criticos.filter(criticidad=criticidad)
        
    if impacto:
        activos_criticos = activos_criticos.filter(impacto_produccion=impacto)
    
    # Crear dataframe para exportar
    data = []
    for activo in activos_criticos:
        data.append({
            'Nombre': activo.nombre,
            'Modelo': activo.modelo,
            'Fabricante': activo.fabricante.nombre,
            'Impacto en Producción': activo.get_impacto_produccion_display(),
            'Disponibilidad de Repuestos': activo.get_disponibilidad_repuestos_display(),
            'Probabilidad de Falla': activo.get_probabilidad_falla_display(),
            'Criticidad': activo.get_criticidad_display(),
            'Estrategia Recomendada': activo.get_estrategia_recomendada_display(),
            'Observaciones': activo.observaciones,
            'Fecha Evaluación': activo.fecha_evaluacion,
            'Responsable': activo.responsable_evaluacion or 'No especificado'
        })
    
    df = pd.DataFrame(data)
    
    # Crear archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Activos Críticos')
    
    # Configurar respuesta HTTP
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=activos_criticos_{timestamp}.xlsx'
    
    return response
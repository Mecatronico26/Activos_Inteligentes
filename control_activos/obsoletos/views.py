# obsoletos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from activos.models import Activo, Fabricante
from .models import ActivoObsoleto
from .forms import ActivoObsoletoForm
import pandas as pd
from io import BytesIO
from django.http import HttpResponse
from datetime import datetime

def obsoleto_list(request):
    """Lista de activos obsoletos"""
    activos_obsoletos = ActivoObsoleto.objects.all()
    
    # Filtrado
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    disponibilidad = request.GET.get('disponibilidad', '')
    
    if query:
        activos_obsoletos = activos_obsoletos.filter(
            Q(nombre__icontains=query) | 
            Q(modelo__icontains=query) |
            Q(fabricante__nombre__icontains=query)
        )
    
    if estado:
        activos_obsoletos = activos_obsoletos.filter(estado_actual=estado)
        
    if disponibilidad:
        activos_obsoletos = activos_obsoletos.filter(disponibilidad_repuestos=disponibilidad)
    
    # Resumen por estado actual
    resumen_estado = (
        ActivoObsoleto.objects
        .values('estado_actual')
        .annotate(count=Count('id'))
        .order_by('estado_actual')
    )
    
    context = {
        'activos_obsoletos': activos_obsoletos,
        'query': query,
        'estado_filter': estado,
        'disponibilidad_filter': disponibilidad,
        'resumen_estado': resumen_estado,
        'estado_choices': ActivoObsoleto.ESTADO_CHOICES,
        'disponibilidad_choices': ActivoObsoleto.DISPONIBILIDAD_CHOICES,
    }
    
    return render(request, 'obsoletos/obsoleto_list.html', context)

def obsoleto_detail(request, pk):
    """Detalle de un activo obsoleto"""
    activo_obsoleto = get_object_or_404(ActivoObsoleto, pk=pk)
    
    # Calcular datos adicionales
    anos_en_servicio = activo_obsoleto.anos_en_servicio()
    porcentaje_vida_util = activo_obsoleto.porcentaje_vida_util_consumida()
    dias_hasta_renovacion = activo_obsoleto.dias_hasta_renovacion() if activo_obsoleto.fecha_renovacion else None
    
    context = {
        'activo_obsoleto': activo_obsoleto,
        'anos_en_servicio': anos_en_servicio,
        'porcentaje_vida_util': porcentaje_vida_util,
        'dias_hasta_renovacion': dias_hasta_renovacion,
    }
    
    return render(request, 'obsoletos/obsoleto_detail.html', context)

def obsoleto_create(request):
    """Crear un nuevo activo obsoleto"""
    if request.method == 'POST':
        form = ActivoObsoletoForm(request.POST)
        if form.is_valid():
            activo_obsoleto = form.save()
            messages.success(request, f'Activo obsoleto {activo_obsoleto.nombre} creado correctamente.')
            return redirect('obsoleto_detail', pk=activo_obsoleto.pk)
    else:
        form = ActivoObsoletoForm()
    
    return render(request, 'obsoletos/obsoleto_form.html', {'form': form, 'title': 'Nuevo Activo Obsoleto'})

def obsoleto_update(request, pk):
    """Actualizar un activo obsoleto existente"""
    activo_obsoleto = get_object_or_404(ActivoObsoleto, pk=pk)
    
    if request.method == 'POST':
        form = ActivoObsoletoForm(request.POST, instance=activo_obsoleto)
        if form.is_valid():
            activo_obsoleto = form.save()
            messages.success(request, f'Activo obsoleto {activo_obsoleto.nombre} actualizado correctamente.')
            return redirect('obsoleto_detail', pk=activo_obsoleto.pk)
    else:
        form = ActivoObsoletoForm(instance=activo_obsoleto)
    
    return render(request, 'obsoletos/obsoleto_form.html', {
        'form': form, 
        'activo_obsoleto': activo_obsoleto,
        'title': 'Editar Activo Obsoleto'
    })

def obsoleto_delete(request, pk):
    """Eliminar un activo obsoleto"""
    activo_obsoleto = get_object_or_404(ActivoObsoleto, pk=pk)
    
    if request.method == 'POST':
        nombre = activo_obsoleto.nombre
        activo_obsoleto.delete()
        messages.success(request, f'Activo obsoleto {nombre} eliminado correctamente.')
        return redirect('obsoleto_list')
    
    return render(request, 'obsoletos/obsoleto_confirm_delete.html', {'activo_obsoleto': activo_obsoleto})

def sincronizar_desde_activos(request):
    """Sincronizar activos obsoletos desde los activos registrados"""
    if request.method == 'POST':
        # Configuración de antigüedad para considerar obsoleto (en años)
        anos_obsolescencia = int(request.POST.get('anos_obsolescencia', 5))
        
        # Obtener activos agrupados por modelo/fabricante con fecha de adquisición antigua
        from django.utils import timezone
        from datetime import timedelta
        
        fecha_limite = timezone.now().date() - timedelta(days=365 * anos_obsolescencia)
        
        activos_antiguos = (
            Activo.objects
            .filter(fecha_adquisicion__lt=fecha_limite)
            .values('modelo', 'fabricante__id', 'fabricante__nombre', 'nombre', 'fecha_adquisicion')
            .annotate(count=Count('id'))
            .order_by('modelo')
        )
        
        nuevos = 0
        existentes = 0
        
        for activo in activos_antiguos:
            fabricante = Fabricante.objects.get(id=activo['fabricante__id'])
            
            # Verificar si ya existe en obsoletos
            obsoleto_existente = ActivoObsoleto.objects.filter(
                modelo=activo['modelo'],
                fabricante=fabricante
            ).first()
            
            if not obsoleto_existente:
                # Extraer el año de instalación
                ano_instalacion = activo['fecha_adquisicion'].year if activo['fecha_adquisicion'] else timezone.now().year - anos_obsolescencia
                
                # Crear nuevo registro de activo obsoleto
                ActivoObsoleto.objects.create(
                    nombre=activo['nombre'],
                    modelo=activo['modelo'],
                    fabricante=fabricante,
                    ano_instalacion=ano_instalacion,
                    vida_util=anos_obsolescencia,
                    estado_actual='obsoleto',
                    disponibilidad_repuestos='baja',
                    estrategia_mitigacion='reemplazo',
                    fecha_renovacion=timezone.now().date() + timedelta(days=180),  # 6 meses
                    presupuesto_estimado=0,
                    impacto_produccion='medio',
                    observaciones='Creado automáticamente desde sincronización de activos antiguos'
                )
                nuevos += 1
            else:
                existentes += 1
        
        messages.success(
            request, 
            f'Sincronización completada. {nuevos} nuevos activos obsoletos creados. {existentes} ya existían.'
        )
        return redirect('obsoleto_list')
    
    return render(request, 'obsoletos/sincronizar_confirm.html')

def exportar_excel(request):
    """Exportar activos obsoletos a Excel"""
    # Obtener datos filtrados si hay parámetros
    activos_obsoletos = ActivoObsoleto.objects.all()
    query = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    disponibilidad = request.GET.get('disponibilidad', '')
    
    if query:
        activos_obsoletos = activos_obsoletos.filter(
            Q(nombre__icontains=query) | 
            Q(modelo__icontains=query) |
            Q(fabricante__nombre__icontains=query)
        )
    
    if estado:
        activos_obsoletos = activos_obsoletos.filter(estado_actual=estado)
        
    if disponibilidad:
        activos_obsoletos = activos_obsoletos.filter(disponibilidad_repuestos=disponibilidad)
    
    # Crear dataframe para exportar
    data = []
    for activo in activos_obsoletos:
        data.append({
            'Nombre': activo.nombre,
            'Modelo': activo.modelo,
            'Fabricante': activo.fabricante.nombre,
            'Año Instalación': activo.ano_instalacion,
            'Vida Útil (años)': activo.vida_util,
            'Años en Servicio': activo.anos_en_servicio(),
            'Estado Actual': activo.get_estado_actual_display(),
            'Disponibilidad Repuestos': activo.get_disponibilidad_repuestos_display(),
            'Estrategia Mitigación': activo.get_estrategia_mitigacion_display(),
            'Fecha Renovación': activo.fecha_renovacion,
            'Presupuesto Estimado': activo.presupuesto_estimado,
            'Impacto Producción': activo.get_impacto_produccion_display(),
            'Observaciones': activo.observaciones,
        })
    
    df = pd.DataFrame(data)
    
    # Crear archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Activos Obsoletos')
    
    # Configurar respuesta HTTP
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=activos_obsoletos_{timestamp}.xlsx'
    
    return response
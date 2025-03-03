# mantenimiento/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from activos.models import Activo, Fabricante
from .models import Mantenimiento, PlanMantenimientoPredictivo, LecturaPredictiva
from .forms import MantenimientoForm, PlanMantenimientoPreditivoForm, LecturaPreditivaForm
import pandas as pd
from io import BytesIO
from django.http import HttpResponse, JsonResponse
from datetime import datetime, timedelta
from django.utils import timezone

def mantenimiento_list(request):
    """Lista de mantenimientos"""
    mantenimientos = Mantenimiento.objects.all()
    
    # Filtrado
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    estado = request.GET.get('estado', '')
    
    if query:
        mantenimientos = mantenimientos.filter(
            Q(nombre__icontains=query) | 
            Q(modelo__icontains=query) |
            Q(fabricante__nombre__icontains=query) |
            Q(responsable__icontains=query)
        )
    
    if tipo:
        mantenimientos = mantenimientos.filter(tipo=tipo)
        
    if estado:
        mantenimientos = mantenimientos.filter(estado=estado)
    
    # Estadísticas
    total_mantenimientos = mantenimientos.count()
    mantenimientos_atrasados = sum(1 for m in mantenimientos if m.esta_atrasado())
    mantenimientos_por_tipo = (
        Mantenimiento.objects
        .values('tipo')
        .annotate(count=Count('id'))
        .order_by('tipo')
    )
    
    mantenimientos_por_estado = (
        Mantenimiento.objects
        .values('estado')
        .annotate(count=Count('id'))
        .order_by('estado')
    )
    
    context = {
        'mantenimientos': mantenimientos,
        'query': query,
        'tipo_filter': tipo,
        'estado_filter': estado,
        'tipo_choices': Mantenimiento.TIPO_CHOICES,
        'estado_choices': Mantenimiento.ESTADO_CHOICES,
        'total_mantenimientos': total_mantenimientos,
        'mantenimientos_atrasados': mantenimientos_atrasados,
        'mantenimientos_por_tipo': mantenimientos_por_tipo,
        'mantenimientos_por_estado': mantenimientos_por_estado,
    }
    
    return render(request, 'mantenimiento/mantenimiento_list.html', context)

def mantenimiento_detail(request, pk):
    """Detalle de un mantenimiento"""
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    
    context = {
        'mantenimiento': mantenimiento,
        'atrasado': mantenimiento.esta_atrasado(),
        'eficiencia_tiempo': mantenimiento.eficiencia_tiempo(),
        'eficiencia_costo': mantenimiento.eficiencia_costo(),
    }
    
    return render(request, 'mantenimiento/mantenimiento_detail.html', context)

def mantenimiento_create(request):
    """Crear un nuevo mantenimiento"""
    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        if form.is_valid():
            mantenimiento = form.save()
            messages.success(request, f'Mantenimiento para {mantenimiento.nombre} creado correctamente.')
            return redirect('mantenimiento_detail', pk=mantenimiento.pk)
    else:
        form = MantenimientoForm()
    
    return render(request, 'mantenimiento/mantenimiento_form.html', {
        'form': form, 
        'title': 'Nuevo Mantenimiento'
    })

def mantenimiento_update(request, pk):
    """Actualizar un mantenimiento existente"""
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    
    if request.method == 'POST':
        form = MantenimientoForm(request.POST, instance=mantenimiento)
        if form.is_valid():
            mantenimiento = form.save()
            messages.success(request, f'Mantenimiento para {mantenimiento.nombre} actualizado correctamente.')
            return redirect('mantenimiento_detail', pk=mantenimiento.pk)
    else:
        form = MantenimientoForm(instance=mantenimiento)
    
    return render(request, 'mantenimiento/mantenimiento_form.html', {
        'form': form, 
        'mantenimiento': mantenimiento,
        'title': 'Editar Mantenimiento'
    })

def mantenimiento_delete(request, pk):
    """Eliminar un mantenimiento"""
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    
    if request.method == 'POST':
        nombre = mantenimiento.nombre
        mantenimiento.delete()
        messages.success(request, f'Mantenimiento para {nombre} eliminado correctamente.')
        return redirect('mantenimiento_list')
    
    return render(request, 'mantenimiento/mantenimiento_confirm_delete.html', {'mantenimiento': mantenimiento})

def completar_mantenimiento(request, pk):
    """Marcar un mantenimiento como completado"""
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    
    if request.method == 'POST':
        # Actualizar estado y fecha de realización
        mantenimiento.estado = 'completado'
        mantenimiento.fecha_realizada = timezone.now().date()
        
        # Capturar datos adicionales
        duracion_real = request.POST.get('duracion_real')
        costo_real = request.POST.get('costo_real')
        observaciones_adicionales = request.POST.get('observaciones_adicionales')
        
        if duracion_real:
            mantenimiento.duracion_real = int(duracion_real)
        
        if costo_real:
            mantenimiento.costo_real = float(costo_real)
        
        if observaciones_adicionales:
            mantenimiento.observaciones = (mantenimiento.observaciones or '') + f"\n\nCompletado el {timezone.now().date()}: {observaciones_adicionales}"
        
        mantenimiento.save()
        messages.success(request, f'Mantenimiento para {mantenimiento.nombre} marcado como completado.')
        return redirect('mantenimiento_detail', pk=pk)
    
    return render(request, 'mantenimiento/completar_mantenimiento.html', {'mantenimiento': mantenimiento})

def posponer_mantenimiento(request, pk):
    """Posponer un mantenimiento para otra fecha"""
    mantenimiento = get_object_or_404(Mantenimiento, pk=pk)
    
    if request.method == 'POST':
        nueva_fecha = request.POST.get('nueva_fecha')
        motivo = request.POST.get('motivo', '')
        
        if nueva_fecha:
            # Actualizar estado y fecha
            mantenimiento.estado = 'pospuesto'
            mantenimiento.fecha_programada = nueva_fecha
            
            # Añadir observación sobre el cambio
            mantenimiento.observaciones = (mantenimiento.observaciones or '') + f"\n\nPospuesto el {timezone.now().date()} para {nueva_fecha}. Motivo: {motivo}"
            
            mantenimiento.save()
            messages.success(request, f'Mantenimiento pospuesto para {nueva_fecha}.')
            return redirect('mantenimiento_detail', pk=pk)
        else:
            messages.error(request, 'Debe proporcionar una nueva fecha.')
    
    return render(request, 'mantenimiento/posponer_mantenimiento.html', {'mantenimiento': mantenimiento})

def programar_desde_activos(request):
    """Programar mantenimientos preventivos para todos los activos"""
    if request.method == 'POST':
        tipo_mantenimiento = request.POST.get('tipo_mantenimiento', 'preventivo')
        dias_futuro = int(request.POST.get('dias_futuro', 30))
        
        # Fecha para programar el mantenimiento
        fecha_programada = timezone.now().date() + timedelta(days=dias_futuro)
        
        # Obtener activos agrupados por modelo/fabricante
        activos_agrupados = (
            Activo.objects
            .values('modelo', 'fabricante__id', 'fabricante__nombre', 'nombre')
            .annotate(count=Count('id'))
            .order_by('modelo')
        )
        
        nuevos = 0
        
        for grupo in activos_agrupados:
            fabricante = Fabricante.objects.get(id=grupo['fabricante__id'])
            
            # Crear mantenimiento programado
            Mantenimiento.objects.create(
                nombre=grupo['nombre'],
                modelo=grupo['modelo'],
                fabricante=fabricante,
                tipo=tipo_mantenimiento,
                fecha_programada=fecha_programada,
                responsable='Por asignar',
                acciones=f'Mantenimiento {tipo_mantenimiento} programado automáticamente',
                estado='programado'
            )
            nuevos += 1
        
        messages.success(
            request, 
            f'Se han programado {nuevos} mantenimientos de tipo {tipo_mantenimiento} para {fecha_programada}.'
        )
        return redirect('mantenimiento_list')
    
    return render(request, 'mantenimiento/programar_confirm.html', {
        'tipo_choices': Mantenimiento.TIPO_CHOICES
    })

def exportar_excel(request):
    """Exportar mantenimientos a Excel"""
    # Obtener datos filtrados si hay parámetros
    mantenimientos = Mantenimiento.objects.all()
    query = request.GET.get('q', '')
    tipo = request.GET.get('tipo', '')
    estado = request.GET.get('estado', '')
    
    if query:
        mantenimientos = mantenimientos.filter(
            Q(nombre__icontains=query) | 
            Q(modelo__icontains=query) |
            Q(fabricante__nombre__icontains=query) |
            Q(responsable__icontains=query)
        )
    
    if tipo:
        mantenimientos = mantenimientos.filter(tipo=tipo)
        
    if estado:
        mantenimientos = mantenimientos.filter(estado=estado)
    
    # Crear dataframe para exportar
    data = []
    for mant in mantenimientos:
        data.append({
            'Nombre': mant.nombre,
            'Modelo': mant.modelo,
            'Fabricante': mant.fabricante.nombre,
            'Tipo': mant.get_tipo_display(),
            'Estado': mant.get_estado_display(),
            'Fecha Programada': mant.fecha_programada,
            'Fecha Realizada': mant.fecha_realizada,
            'Responsable': mant.responsable,
            'Acciones': mant.acciones,
            'Duración Estimada (min)': mant.duracion_estimada,
            'Duración Real (min)': mant.duracion_real,
            'Costo Estimado': mant.costo_estimado,
            'Costo Real': mant.costo_real,
            'Observaciones': mant.observaciones,
        })
    
    df = pd.DataFrame(data)
    
    # Crear archivo Excel en memoria
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Mantenimientos')
    
    # Configurar respuesta HTTP
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    response = HttpResponse(
        output.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename=mantenimientos_{timestamp}.xlsx'
    
    return response

# Vistas para mantenimiento predictivo
def plan_predictivo_list(request):
    """Lista de planes de mantenimiento predictivo"""
    planes = PlanMantenimientoPredictivo.objects.all()
    
    context = {
        'planes': planes,
    }
    
    return render(request, 'mantenimiento/plan_predictivo_list.html', context)

def plan_predictivo_detail(request, pk):
    """Detalle de un plan de mantenimiento predictivo"""
    plan = get_object_or_404(PlanMantenimientoPredictivo, pk=pk)
    lecturas = plan.lecturas.all().order_by('-fecha_lectura')
    
    # Datos para gráfica
    if lecturas:
        lecturas_data = {
            'fechas': [l.fecha_lectura.strftime('%Y-%m-%d') for l in lecturas],
            'valores': [l.valor_medido for l in lecturas],
            'umbral': plan.valor_umbral
        }
    else:
        lecturas_data = None
    
    context = {
        'plan': plan,
        'lecturas': lecturas,
        'lecturas_data': lecturas_data,
    }
    
    return render(request, 'mantenimiento/plan_predictivo_detail.html', context)

def plan_predictivo_create(request):
    """Crear un nuevo plan de mantenimiento predictivo"""
    if request.method == 'POST':
        form = PlanMantenimientoPreditivoForm(request.POST)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Plan predictivo {plan.nombre_plan} creado correctamente.')
            return redirect('plan_predictivo_detail', pk=plan.pk)
    else:
        form = PlanMantenimientoPreditivoForm()
    
    return render(request, 'mantenimiento/plan_predictivo_form.html', {
        'form': form, 
        'title': 'Nuevo Plan de Mantenimiento Predictivo'
    })

def plan_predictivo_update(request, pk):
    """Actualizar un plan de mantenimiento predictivo"""
    plan = get_object_or_404(PlanMantenimientoPredictivo, pk=pk)
    
    if request.method == 'POST':
        form = PlanMantenimientoPreditivoForm(request.POST, instance=plan)
        if form.is_valid():
            plan = form.save()
            messages.success(request, f'Plan predictivo {plan.nombre_plan} actualizado correctamente.')
            return redirect('plan_predictivo_detail', pk=plan.pk)
    else:
        form = PlanMantenimientoPreditivoForm(instance=plan)
    
    return render(request, 'mantenimiento/plan_predictivo_form.html', {
        'form': form, 
        'plan': plan,
        'title': 'Editar Plan de Mantenimiento Predictivo'
    })

def plan_predictivo_delete(request, pk):
    """Eliminar un plan de mantenimiento predictivo"""
    plan = get_object_or_404(PlanMantenimientoPredictivo, pk=pk)
    
    if request.method == 'POST':
        nombre = plan.nombre_plan
        plan.delete()
        messages.success(request, f'Plan predictivo {nombre} eliminado correctamente.')
        return redirect('plan_predictivo_list')
    
    return render(request, 'mantenimiento/plan_predictivo_confirm_delete.html', {'plan': plan})

def lectura_predictiva_create(request, plan_id):
    """Registrar una nueva lectura predictiva"""
    plan = get_object_or_404(PlanMantenimientoPredictivo, pk=plan_id)
    
    if request.method == 'POST':
        form = LecturaPreditivaForm(request.POST)
        if form.is_valid():
            lectura = form.save(commit=False)
            lectura.plan = plan
            lectura.save()
            
            # Verificar si supera el umbral para generar alerta
            if lectura.supera_umbral:
                messages.warning(
                    request, 
                    f'¡Alerta! La lectura de {lectura.valor_medido} {plan.unidad_medida} '
                    f'supera el umbral establecido de {plan.valor_umbral} {plan.unidad_medida}.'
                )
                
                # Opcionalmente crear un mantenimiento correctivo
                crear_mantenimiento = request.POST.get('crear_mantenimiento') == 'on'
                if crear_mantenimiento:
                    activo = plan.activo
                    
                    Mantenimiento.objects.create(
                        nombre=activo.nombre,
                        modelo=activo.modelo,
                        fabricante=activo.fabricante,
                        activo=activo,
                        tipo='correctivo',
                        fecha_programada=timezone.now().date() + timedelta(days=1),  # Mañana
                        responsable=lectura.responsable,
                        acciones=f'Mantenimiento correctivo generado automáticamente por lectura predictiva que supera el umbral. '
                                f'Lectura: {lectura.valor_medido} {plan.unidad_medida}, '
                                f'Umbral: {plan.valor_umbral} {plan.unidad_medida}',
                        estado='programado',
                        requiere_parada=True,
                    )
                    messages.success(
                        request,
                        'Se ha generado automáticamente un mantenimiento correctivo con prioridad alta.'
                    )
            else:
                messages.success(request, 'Lectura registrada correctamente.')
                
            return redirect('plan_predictivo_detail', pk=plan_id)
    else:
        form = LecturaPreditivaForm()
    
    return render(request, 'mantenimiento/lectura_predictiva_form.html', {
        'form': form,
        'plan': plan,
    })

def obtener_datos_predictivos(request, plan_id):
    """API para obtener datos de lecturas predictivas para gráficas"""
    plan = get_object_or_404(PlanMantenimientoPredictivo, pk=plan_id)
    lecturas = plan.lecturas.all().order_by('fecha_lectura')
    
    datos = {
        'fechas': [l.fecha_lectura.strftime('%Y-%m-%d %H:%M') for l in lecturas],
        'valores': [l.valor_medido for l in lecturas],
        'umbral': plan.valor_umbral,
        'unidad': plan.unidad_medida,
    }
    
    return JsonResponse(datos)
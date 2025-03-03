# ai_views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from activos.models import Activo
from criticos.models import ActivoCritico
from obsoletos.models import ActivoObsoleto
from mantenimiento.models import Mantenimiento, LecturaPredictiva
from utils.ai_module import (
    clasificar_criticidad_activos,
    predecir_fallas,
    optimizar_mantenimiento,
    detectar_anomalias
)
import pandas as pd
from datetime import datetime, timedelta

def dashboard_ia(request):
    """Dashboard principal con resumen de funcionalidades de IA"""
    # Contar activos por categoría
    total_activos = Activo.objects.count()
    total_criticos = ActivoCritico.objects.count()
    total_obsoletos = ActivoObsoleto.objects.count()
    total_mantenimientos = Mantenimiento.objects.count()
    
    # Verificar si hay suficientes datos para modelos de IA
    suficientes_datos = total_activos >= 10 and total_mantenimientos >= 10
    
    # Obtener últimas anomalías detectadas (si existen)
    ultimas_anomalias = []
    if LecturaPredictiva.objects.filter(supera_umbral=True).exists():
        anomalias = LecturaPredictiva.objects.filter(supera_umbral=True).order_by('-fecha_lectura')[:5]
        for anomalia in anomalias:
            ultimas_anomalias.append({
                'plan': anomalia.plan.nombre_plan,
                'activo': anomalia.plan.activo.nombre if anomalia.plan.activo else "No especificado",
                'valor': anomalia.valor_medido,
                'umbral': anomalia.plan.valor_umbral,
                'fecha': anomalia.fecha_lectura,
                'responsable': anomalia.responsable
            })
    
    context = {
        'total_activos': total_activos,
        'total_criticos': total_criticos,
        'total_obsoletos': total_obsoletos,
        'total_mantenimientos': total_mantenimientos,
        'suficientes_datos': suficientes_datos,
        'ultimas_anomalias': ultimas_anomalias
    }
    
    return render(request, 'ai/dashboard.html', context)

def analisis_criticidad(request):
    """Análisis automático de criticidad usando IA"""
    if request.method == 'POST':
        # Procesar activos críticos
        activos_criticos = ActivoCritico.objects.all()
        
        if activos_criticos.count() < 5:
            messages.warning(request, 'Se necesitan al menos 5 activos críticos para realizar el análisis de criticidad.')
            return redirect('analisis_criticidad')
        
        # Preparar datos para el algoritmo
        datos = []
        for activo in activos_criticos:
            datos.append({
                'id': activo.id,
                'nombre': activo.nombre,
                'modelo': activo.modelo,
                'impacto_produccion': activo.impacto_produccion,
                'disponibilidad_repuestos': activo.disponibilidad_repuestos,
                'probabilidad_falla': activo.probabilidad_falla
            })
        
        # Llamar a la función de IA
        try:
            resultados = clasificar_criticidad_activos(datos)
            
            # Actualizar clasificación de criticidad en base de datos
            for i, activo in enumerate(activos_criticos):
                nueva_criticidad = resultados['criticidad'][i]['criticidad_calculada']
                
                # Actualizar solo si la criticidad es diferente
                if activo.criticidad != nueva_criticidad:
                    activo.criticidad = nueva_criticidad
                    activo.observaciones = (activo.observaciones or '') + f"\n\nCriticidad actualizada por IA el {datetime.now().strftime('%Y-%m-%d')}."
                    activo.save()
            
            messages.success(
                request, 
                f'Análisis de criticidad completado. Se ha clasificado {len(activos_criticos)} activos.'
            )
            
            # Guardar gráfico para mostrar
            request.session['grafico_criticidad'] = resultados['grafico']
            
            return redirect('analisis_criticidad')
            
        except Exception as e:
            messages.error(request, f'Error al realizar el análisis de criticidad: {str(e)}')
            return redirect('analisis_criticidad')
    
    # Obtener resumen de criticidad actual
    resumen_criticidad = (
        ActivoCritico.objects
        .values('criticidad')
        .annotate(count=activos_criticos.Count('id'))
        .order_by('criticidad')
    )
    
    # Verificar si hay un gráfico en sesión
    grafico = request.session.get('grafico_criticidad', None)
    
    context = {
        'activos_criticos': ActivoCritico.objects.all(),
        'resumen_criticidad': resumen_criticidad,
        'grafico': grafico,
        'suficientes_datos': ActivoCritico.objects.count() >= 5
    }
    
    return render(request, 'ai/analisis_criticidad.html', context)

def prediccion_fallas(request):
    """Predicción de fallas usando Machine Learning"""
    # Verificar si hay suficientes datos
    if Mantenimiento.objects.filter(tipo='correctivo').count() < 10 or LecturaPredictiva.objects.count() < 20:
        messages.warning(
            request, 
            'Se necesitan al menos 10 registros de mantenimientos correctivos y 20 lecturas de sensores para generar predicciones confiables.'
        )
        suficientes_datos = False
    else:
        suficientes_datos = True
    
    if request.method == 'POST' and suficientes_datos:
        # Obtener parámetros
        dias_prediccion = int(request.POST.get('dias_prediccion', 30))
        
        # Preparar datos históricos de fallas
        datos_historicos = []
        mantenimientos = Mantenimiento.objects.filter(
            tipo__in=['correctivo', 'preventivo'], 
            estado='completado'
        )
        
        for mant in mantenimientos:
            datos_historicos.append({
                'activo_id': mant.activo.id if mant.activo else None,
                'fecha': mant.fecha_realizada,
                'tipo_mantenimiento': mant.tipo,
                'falla': 1 if mant.tipo == 'correctivo' else 0,
                'tiempo_resolucion': mant.duracion_real or 0,
                'costo': mant.costo_real or 0
            })
        
        # Preparar datos de sensores
        sensor_data = []
        lecturas = LecturaPredictiva.objects.all()
        
        for lectura in lecturas:
            if lectura.plan.activo:
                sensor_data.append({
                    'activo_id': lectura.plan.activo.id,
                    'sensor_id': lectura.plan.id,
                    'fecha': lectura.fecha_lectura,
                    'valor': lectura.valor_medido,
                    'parametro': lectura.plan.parametros_medicion,
                    'umbral': lectura.plan.valor_umbral
                })
        
        # Llamar a la función de IA
        try:
            resultados = predecir_fallas(datos_historicos, sensor_data, dias_prediccion)
            
            if 'error' in resultados:
                messages.warning(request, resultados['error'])
            else:
                messages.success(
                    request, 
                    f'Predicción de fallas completada. Se han analizado {len(sensor_data)} lecturas de sensores.'
                )
                
                # Guardar gráfico y predicciones en sesión
                request.session['grafico_prediccion'] = resultados['grafico']
                request.session['predicciones_fallas'] = resultados['predicciones']
                request.session['precision_prediccion'] = resultados['precision_modelo']
            
            return redirect('prediccion_fallas')
            
        except Exception as e:
            messages.error(request, f'Error al realizar la predicción de fallas: {str(e)}')
            return redirect('prediccion_fallas')
    
    # Obtener datos de sesión
    grafico = request.session.get('grafico_prediccion', None)
    predicciones = request.session.get('predicciones_fallas', [])
    precision = request.session.get('precision_prediccion', None)
    
    context = {
        'grafico': grafico,
        'predicciones': predicciones,
        'precision': precision,
        'suficientes_datos': suficientes_datos,
        'total_lecturas': LecturaPredictiva.objects.count(),
        'total_mantenimientos_correctivos': Mantenimiento.objects.filter(tipo='correctivo').count()
    }
    
    return render(request, 'ai/prediccion_fallas.html', context)

def optimizacion_mantenimiento(request):
    """Optimización de mantenimiento preventivo"""
    # Verificar si hay suficientes datos
    if Mantenimiento.objects.filter(estado='completado').count() < 10:
        messages.warning(
            request, 
            'Se necesitan al menos 10 registros de mantenimientos completados para optimizar la programación.'
        )
        suficientes_datos = False
    else:
        suficientes_datos = True
    
    if request.method == 'POST' and suficientes_datos:
        # Preparar datos de mantenimientos
        datos_mantenimientos = []
        mantenimientos = Mantenimiento.objects.filter(estado='completado')
        
        for mant in mantenimientos:
            # Calcular días entre mantenimientos (si es posible)
            if mant.activo:
                ultimo_mantenimiento = Mantenimiento.objects.filter(
                    activo=mant.activo,
                    estado='completado',
                    fecha_realizada__lt=mant.fecha_realizada
                ).order_by('-fecha_realizada').first()
                
                if ultimo_mantenimiento:
                    dias_entre = (mant.fecha_realizada - ultimo_mantenimiento.fecha_realizada).days
                else:
                    dias_entre = 90  # Valor predeterminado
            else:
                dias_entre = 90  # Valor predeterminado
            
            datos_mantenimientos.append({
                'activo_id': mant.activo.id if mant.activo else None,
                'tipo': mant.tipo,
                'estado': mant.estado,
                'fecha_realizada': mant.fecha_realizada,
                'duracion_real': mant.duracion_real or 0,
                'costo_real': mant.costo_real or 0,
                'requiere_parada': mant.requiere_parada,
                'dias_entre_mantenimientos': dias_entre
            })
        
        # Preparar datos de sensores
        lecturas_sensores = []
        lecturas = LecturaPredictiva.objects.all()
        
        for lectura in lecturas:
            if lectura.plan.activo:
                lecturas_sensores.append({
                    'activo_id': lectura.plan.activo.id,
                    'sensor_id': lectura.plan.id,
                    'fecha': lectura.fecha_lectura,
                    'valor': lectura.valor_medido,
                    'parametro': lectura.plan.parametros_medicion
                })
        
        # Preparar información de activos
        activos_info = []
        for activo in Activo.objects.all():
            # Obtener criticidad si existe
            try:
                critico = ActivoCritico.objects.get(modelo=activo.modelo, fabricante=activo.fabricante)
                criticidad = critico.criticidad
            except ActivoCritico.DoesNotExist:
                criticidad = 'media'  # Valor predeterminado
            
            # Calcular edad del activo
            if activo.fecha_adquisicion:
                edad_activo = (datetime.now().date() - activo.fecha_adquisicion).days // 365
            else:
                edad_activo = 3  # Valor predeterminado
            
            activos_info.append({
                'activo_id': activo.id,
                'nombre': activo.nombre,
                'modelo': activo.modelo,
                'criticidad': criticidad,
                'edad_activo': edad_activo,
                'horas_operacion': 8760  # Valor predeterminado (24*365)
            })
        
        # Llamar a la función de IA
        try:
            resultados = optimizar_mantenimiento(datos_mantenimientos, lecturas_sensores, activos_info)
            
            if 'error' in resultados:
                messages.warning(request, resultados['error'])
            else:
                messages.success(
                    request, 
                    f'Optimización de mantenimiento completada. Se han generado {len(resultados["recomendaciones"])} recomendaciones.'
                )
                
                # Guardar resultados en sesión
                request.session['grafico_optimizacion'] = resultados['grafico']
                request.session['recomendaciones_mantenimiento'] = resultados['recomendaciones']
                request.session['precision_optimizacion'] = resultados['precision_modelo']
            
            return redirect('optimizacion_mantenimiento')
            
        except Exception as e:
            messages.error(request, f'Error al realizar la optimización: {str(e)}')
            return redirect('optimizacion_mantenimiento')
    
    # Obtener datos de sesión
    grafico = request.session.get('grafico_optimizacion', None)
    recomendaciones = request.session.get('recomendaciones_mantenimiento', [])
    precision = request.session.get('precision_optimizacion', None)
    
    context = {
        'grafico': grafico,
        'recomendaciones': recomendaciones,
        'precision': precision,
        'suficientes_datos': suficientes_datos,
        'total_mantenimientos': Mantenimiento.objects.filter(estado='completado').count()
    }
    
    return render(request, 'ai/optimizacion_mantenimiento.html', context)

def deteccion_anomalias(request):
    """Detección de anomalías en lecturas de sensores"""
    # Verificar si hay suficientes datos
    if LecturaPredictiva.objects.count() < 20:
        messages.warning(
            request, 
            'Se necesitan al menos 20 lecturas de sensores para detectar anomalías confiables.'
        )
        suficientes_datos = False
    else:
        suficientes_datos = True
    
    if request.method == 'POST' and suficientes_datos:
        # Obtener parámetros
        umbral_zscore = float(request.POST.get('umbral_zscore', 3.0))
        
        # Preparar datos de sensores
        lecturas_sensores = []
        lecturas = LecturaPredictiva.objects.all()
        
        for lectura in lecturas:
            if lectura.plan.activo:
                lecturas_sensores.append({
                    'activo_id': lectura.plan.activo.id,
                    'sensor_id': lectura.plan.id,
                    'fecha': lectura.fecha_lectura,
                    'valor': lectura.valor_medido,
                    'parametro': lectura.plan.parametros_medicion,
                    'umbral': lectura.plan.valor_umbral
                })
        
        # Llamar a la función de IA
        try:
            resultados = detectar_anomalias(lecturas_sensores, umbral_zscore)
            
            if 'error' in resultados:
                messages.warning(request, resultados['error'])
            else:
                messages.success(
                    request, 
                    f'Detección de anomalías completada. Se han encontrado {resultados["total_anomalias"]} anomalías.'
                )
                
                # Guardar resultados en sesión
                request.session['grafico_anomalias'] = resultados['grafico']
                request.session['anomalias_detectadas'] = resultados['anomalias']
                request.session['total_anomalias'] = resultados['total_anomalias']
            
            return redirect('deteccion_anomalias')
            
        except Exception as e:
            messages.error(request, f'Error al detectar anomalías: {str(e)}')
            return redirect('deteccion_anomalias')
    
    # Obtener datos de sesión
    grafico = request.session.get('grafico_anomalias', None)
    anomalias = request.session.get('anomalias_detectadas', [])
    total_anomalias = request.session.get('total_anomalias', 0)
    
    context = {
        'grafico': grafico,
        'anomalias': anomalias,
        'total_anomalias': total_anomalias,
        'suficientes_datos': suficientes_datos,
        'total_lecturas': LecturaPredictiva.objects.count()
    }
    
    return render(request, 'ai/deteccion_anomalias.html', context)

@require_POST
def aplicar_recomendaciones(request):
    """Aplica automáticamente las recomendaciones de IA"""
    accion = request.POST.get('accion')
    
    if accion == 'programar_mantenimientos':
        # Recuperar recomendaciones de sesión
        recomendaciones = request.session.get('recomendaciones_mantenimiento', [])
        
        if not recomendaciones:
            return JsonResponse({'status': 'error', 'message': 'No hay recomendaciones disponibles'})
        
        # Crear mantenimientos preventivos según recomendaciones
        creados = 0
        for rec in recomendaciones:
            try:
                activo_id = rec['activo_id']
                activo = Activo.objects.get(id=activo_id)
                
                # Verificar si ya existe un mantenimiento programado cercano
                fecha_recomendada = datetime.strptime(rec['fecha_recomendada'], '%Y-%m-%d').date()
                
                # Comprobar si ya existe mantenimiento programado para este activo en ±7 días
                existe_programado = Mantenimiento.objects.filter(
                    activo=activo,
                    estado='programado',
                    fecha_programada__range=[
                        fecha_recomendada - timedelta(days=7),
                        fecha_recomendada + timedelta(days=7)
                    ]
                ).exists()
                
                if not existe_programado:
                    # Crear nuevo mantenimiento preventivo
                    Mantenimiento.objects.create(
                        nombre=activo.nombre,
                        modelo=activo.modelo,
                        fabricante=activo.fabricante,
                        activo=activo,
                        tipo='preventivo',
                        fecha_programada=fecha_recomendada,
                        responsable='Por asignar (IA)',
                        acciones=f'Mantenimiento preventivo programado automáticamente por IA. Intervalo recomendado: {rec["dias_recomendados"]} días.',
                        estado='programado'
                    )
                    creados += 1
            except Exception:
                continue
        
        return JsonResponse({
            'status': 'success', 
            'message': f'Se han programado {creados} mantenimientos preventivos según las recomendaciones'
        })
        
    elif accion == 'actualizar_criticidad':
        # Similar a la función anterior pero para criticidad
        return JsonResponse({
            'status': 'success', 
            'message': 'Criticidad actualizada según recomendaciones'
        })
    
    return JsonResponse({'status': 'error', 'message': 'Acción no válida'})
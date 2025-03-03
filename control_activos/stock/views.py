# stock/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count
from activos.models import Activo, Fabricante
from .models import StockActivo, MovimientoStock
from .forms import StockActivoForm, MovimientoStockForm
from django.db.models import Q

def stock_list(request):
    """Lista de activos en stock con conteo automático"""
    stock_activos = StockActivo.objects.all()
    
    # Filtrado
    query = request.GET.get('q', '')
    if query:
        stock_activos = stock_activos.filter(
            Q(nombre__icontains=query) | 
            Q(modelo__icontains=query) |
            Q(fabricante__nombre__icontains=query)
        )
    
    # Estados de stock
    stock_bajo = stock_activos.filter(cantidad__lt=1).count()
    stock_critico = stock_activos.filter(cantidad__gte=1, cantidad__lt=2).count()
    stock_normal = stock_activos.filter(cantidad__gte=2).count()
    
    context = {
        'stock_activos': stock_activos,
        'query': query,
        'stock_bajo': stock_bajo,
        'stock_critico': stock_critico,
        'stock_normal': stock_normal,
    }
    
    return render(request, 'stock/stock_list.html', context)

def stock_detail(request, pk):
    """Detalle de un activo en stock con historial de movimientos"""
    stock_activo = get_object_or_404(StockActivo, pk=pk)
    movimientos = stock_activo.movimientos.all().order_by('-fecha')
    
    context = {
        'stock_activo': stock_activo,
        'movimientos': movimientos,
    }
    
    return render(request, 'stock/stock_detail.html', context)

def stock_create(request):
    """Crear un nuevo activo en stock"""
    if request.method == 'POST':
        form = StockActivoForm(request.POST)
        if form.is_valid():
            stock_activo = form.save()
            messages.success(request, f'Stock para {stock_activo.nombre} creado correctamente.')
            
            # Crear un movimiento inicial si hay cantidad
            if stock_activo.cantidad > 0:
                MovimientoStock.objects.create(
                    stock_activo=stock_activo,
                    tipo='entrada',
                    cantidad=stock_activo.cantidad,
                    responsable=request.user.username if request.user.is_authenticated else 'Sistema',
                    comentarios='Inventario inicial'
                )
            
            return redirect('stock_detail', pk=stock_activo.pk)
    else:
        form = StockActivoForm()
    
    return render(request, 'stock/stock_form.html', {'form': form, 'title': 'Nuevo Stock'})

def stock_update(request, pk):
    """Actualizar un activo en stock"""
    stock_activo = get_object_or_404(StockActivo, pk=pk)
    
    if request.method == 'POST':
        form = StockActivoForm(request.POST, instance=stock_activo)
        if form.is_valid():
            # Guardar cantidad anterior para comparar
            cantidad_anterior = stock_activo.cantidad
            stock_activo = form.save()
            
            # Si cambió la cantidad, registrar movimiento
            nueva_cantidad = stock_activo.cantidad
            if nueva_cantidad != cantidad_anterior:
                diferencia = nueva_cantidad - cantidad_anterior
                tipo = 'entrada' if diferencia > 0 else 'salida'
                
                MovimientoStock.objects.create(
                    stock_activo=stock_activo,
                    tipo=tipo,
                    cantidad=abs(diferencia),
                    responsable=request.user.username if request.user.is_authenticated else 'Sistema',
                    comentarios='Ajuste manual de inventario'
                )
            
            messages.success(request, f'Stock para {stock_activo.nombre} actualizado correctamente.')
            return redirect('stock_detail', pk=stock_activo.pk)
    else:
        form = StockActivoForm(instance=stock_activo)
    
    return render(request, 'stock/stock_form.html', {
        'form': form, 
        'stock_activo': stock_activo,
        'title': 'Editar Stock'
    })

def stock_delete(request, pk):
    """Eliminar un activo de stock"""
    stock_activo = get_object_or_404(StockActivo, pk=pk)
    
    if request.method == 'POST':
        nombre = stock_activo.nombre
        stock_activo.delete()
        messages.success(request, f'Stock para {nombre} eliminado correctamente.')
        return redirect('stock_list')
    
    return render(request, 'stock/stock_confirm_delete.html', {'stock_activo': stock_activo})

def nuevo_movimiento(request, stock_id):
    """Registrar un nuevo movimiento de stock"""
    stock_activo = get_object_or_404(StockActivo, pk=stock_id)
    
    if request.method == 'POST':
        form = MovimientoStockForm(request.POST)
        if form.is_valid():
            movimiento = form.save(commit=False)
            movimiento.stock_activo = stock_activo
            
            # Actualizar cantidad en stock
            if movimiento.tipo == 'entrada':
                stock_activo.cantidad += movimiento.cantidad
            elif movimiento.tipo == 'salida':
                # Verificar que haya suficiente stock
                if stock_activo.cantidad < movimiento.cantidad:
                    messages.error(request, f'Error: No hay suficiente stock. Disponible: {stock_activo.cantidad}')
                    return redirect('nuevo_movimiento', stock_id=stock_id)
                
                stock_activo.cantidad -= movimiento.cantidad
            
            # Guardar cambios
            stock_activo.save()
            movimiento.save()
            
            messages.success(request, f'Movimiento de {movimiento.get_tipo_display()} registrado correctamente.')
            return redirect('stock_detail', pk=stock_id)
    else:
        form = MovimientoStockForm()
    
    context = {
        'form': form,
        'stock_activo': stock_activo,
    }
    
    return render(request, 'stock/movimiento_form.html', context)

def sincronizar_desde_activos(request):
    """Sincronizar stock desde los activos registrados"""
    if request.method == 'POST':
        # Obtener activos agrupados por modelo/fabricante
        activos_agrupados = (
            Activo.objects
            .values('modelo', 'fabricante__id', 'fabricante__nombre', 'nombre')
            .annotate(count=Count('id'))
            .order_by('modelo')
        )
        
        nuevos = 0
        actualizados = 0
        
        for grupo in activos_agrupados:
            fabricante = Fabricante.objects.get(id=grupo['fabricante__id'])
            
            # Buscar si ya existe en stock
            stock_existente = StockActivo.objects.filter(
                modelo=grupo['modelo'],
                fabricante=fabricante
            ).first()
            
            if stock_existente:
                # Actualizar cantidad si es necesario
                if stock_existente.cantidad != grupo['count']:
                    stock_existente.cantidad = grupo['count']
                    stock_existente.save()
                    actualizados += 1
            else:
                # Crear nuevo registro de stock
                StockActivo.objects.create(
                    nombre=grupo['nombre'],
                    modelo=grupo['modelo'],
                    fabricante=fabricante,
                    cantidad=grupo['count']
                )
                nuevos += 1
        
        messages.success(
            request, 
            f'Sincronización completada. {nuevos} nuevos registros creados, {actualizados} actualizados.'
        )
        return redirect('stock_list')
    
    return render(request, 'stock/sincronizar_confirm.html')
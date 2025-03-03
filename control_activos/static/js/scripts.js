// static/js/scripts.js
// Scripts personalizados para el Sistema de Control de Activos

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar componentes
    console.log('Sistema de Control de Activos iniciado');
    
    // Inicializar tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
    
    // Inicializar popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });
    
    // Inicializar validación de formularios
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
    
    // Configurar desaparición automática de alertas
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Función para manejar la actualización de subáreas al cambiar el área
    actualizarSubareas();
    
    // Inicializar previsualización de imágenes
    inicializarPrevisualizacionImagen();
    
    // Inicializar DataTables
    inicializarDataTables();
    
    // Inicializar gráficos
    inicializarGraficos();
});

// Función para manejar la actualización de subáreas al cambiar el área
function actualizarSubareas() {
    const areaSelect = document.getElementById('id_area_select');
    const subareaSelect = document.getElementById('id_subarea_select');
    
    if (areaSelect && subareaSelect) {
        areaSelect.addEventListener('change', function() {
            const areaId = this.value;
            
            // Limpiar select de subáreas
            subareaSelect.innerHTML = '<option value="">---------</option>';
            
            if (areaId) {
                // Realizar petición AJAX para obtener subáreas
                fetch(`/activos/api/get-subareas/?area_id=${areaId}`)
                    .then(response => response.json())
                    .then(data => {
                        data.forEach(subarea => {
                            const option = document.createElement('option');
                            option.value = subarea.id;
                            option.textContent = subarea.nombre;
                            subareaSelect.appendChild(option);
                        });
                    })
                    .catch(error => {
                        console.error('Error al obtener subáreas:', error);
                    });
            }
        });
    }
}

// Función para previsualizar imágenes antes de subir
function inicializarPrevisualizacionImagen() {
    const imageInput = document.getElementById('id_imagen');
    const previewContainer = document.getElementById('preview-container');
    
    if (imageInput && previewContainer) {
        imageInput.addEventListener('change', function() {
            previewContainer.innerHTML = '';
            
            if (this.files && this.files[0]) {
                const file = this.files[0];
                
                // Verificar que sea una imagen
                if (!file.type.match('image.*')) {
                    previewContainer.innerHTML = '<div class="alert alert-warning">El archivo seleccionado no es una imagen.</div>';
                    return;
                }
                
                const reader = new FileReader();
                
                reader.onload = function(e) {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'img-fluid image-preview';
                    previewContainer.appendChild(img);
                }
                
                reader.readAsDataURL(file);
            }
        });
    }
}

// Función para inicializar todas las DataTables
function inicializarDataTables() {
    $('.datatable').each(function() {
        const options = {
            language: {
                url: '//cdn.datatables.net/plug-ins/1.12.1/i18n/es-ES.json'
            },
            pageLength: 25,
            responsive: true
        };
        
        // Si tiene el atributo data-order, configurar ordenamiento
        if ($(this).attr('data-order')) {
            const orderConfig = JSON.parse($(this).attr('data-order'));
            options.order = orderConfig;
        }
        
        // Si tiene el atributo data-paging, configurar paginación
        if ($(this).attr('data-paging') === 'false') {
            options.paging = false;
        }
        
        // Si tiene el atributo data-export, añadir botones de exportación
        if ($(this).attr('data-export') === 'true') {
            options.dom = 'Bfrtip';
            options.buttons = [
                'copy', 'csv', 'excel', 'pdf', 'print'
            ];
        }
        
        $(this).DataTable(options);
    });
}

// Función para inicializar gráficos
function inicializarGraficos() {
    // Gráficos de criticidad
    const criticidadChartEl = document.getElementById('criticidad-chart');
    if (criticidadChartEl) {
        const ctx = criticidadChartEl.getContext('2d');
        
        // Obtener datos del elemento data-chart
        const chartData = JSON.parse(criticidadChartEl.getAttribute('data-chart'));
        
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.data,
                    backgroundColor: [
                        '#28a745', // Baja
                        '#17a2b8', // Media
                        '#ffc107', // Alta
                        '#dc3545'  // Extrema
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    title: {
                        display: true,
                        text: 'Distribución de Criticidad'
                    }
                }
            }
        });
    }
    
    // Gráficos de mantenimiento
    const mantenimientoChartEl = document.getElementById('mantenimiento-chart');
    if (mantenimientoChartEl) {
        const ctx = mantenimientoChartEl.getContext('2d');
        
        // Obtener datos del elemento data-chart
        const chartData = JSON.parse(mantenimientoChartEl.getAttribute('data-chart'));
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: chartData.labels,
                datasets: [{
                    label: chartData.title,
                    data: chartData.data,
                    backgroundColor: chartData.colors || '#0d6efd',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Gráficos de lecturas predictivas
    const lecturaChartEl = document.getElementById('lectura-chart');
    if (lecturaChartEl) {
        const ctx = lecturaChartEl.getContext('2d');
        
        // Obtener datos del elemento data-chart
        const chartData = JSON.parse(lecturaChartEl.getAttribute('data-chart'));
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.fechas,
                datasets: [{
                    label: 'Valor medido',
                    data: chartData.valores,
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.1)',
                    tension: 0.2,
                    fill: true
                }, {
                    label: 'Umbral',
                    data: Array(chartData.fechas.length).fill(chartData.umbral),
                    borderColor: '#dc3545',
                    borderDash: [5, 5],
                    fill: false,
                    pointRadius: 0
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    },
                    title: {
                        display: true,
                        text: 'Historial de Lecturas'
                    }
                },
                scales: {
                    y: {
                        title: {
                            display: true,
                            text: chartData.unidad || 'Valor'
                        }
                    }
                }
            }
        });
    }
}

// Función para confirmar eliminación
function confirmarEliminacion(event, mensaje = '¿Está seguro de que desea eliminar este elemento?') {
    if (!confirm(mensaje)) {
        event.preventDefault();
        return false;
    }
    return true;
}

// Función para aplicar filtros en tablas
function aplicarFiltros(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.submit();
    }
}

// Función para restablecer filtros
function restablecerFiltros(formId) {
    const form = document.getElementById(formId);
    if (form) {
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(input => {
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            } else {
                input.value = '';
            }
        });
        form.submit();
    }
}

// Función para aplicar recomendaciones de IA
function aplicarRecomendacionesIA(accion) {
    // Mostrar spinner
    document.getElementById('spinner-aplicar').classList.remove('d-none');
    
    // Realizar petición AJAX
    fetch('/aplicar-recomendaciones/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: `accion=${accion}`
    })
    .then(response => response.json())
    .then(data => {
        // Ocultar spinner
        document.getElementById('spinner-aplicar').classList.add('d-none');
        
        // Mostrar mensaje
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${data.status === 'success' ? 'success' : 'danger'} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${data.message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.getElementById('alertas-container').appendChild(alertDiv);
        
        // Recargar página después de 2 segundos si fue exitoso
        if (data.status === 'success') {
            setTimeout(() => {
                window.location.reload();
            }, 2000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('spinner-aplicar').classList.add('d-none');
        
        // Mostrar mensaje de error
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            Error al aplicar recomendaciones. Por favor, inténtelo de nuevo.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.getElementById('alertas-container').appendChild(alertDiv);
    });
}

// Función para exportar a Excel
function exportarExcel(url) {
    window.location.href = url;
}

// Función para completar mantenimiento
function completarMantenimiento(id) {
    window.location.href = `/mantenimiento/${id}/completar/`;
}

// Función para posponer mantenimiento
function posponerMantenimiento(id) {
    window.location.href = `/mantenimiento/${id}/posponer/`;
}
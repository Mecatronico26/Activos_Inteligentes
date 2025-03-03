# utils/constants.py
"""
Constantes y configuraciones para el sistema de Control de Activos
"""

# Configuración general
APP_NAME = "Sistema de Control de Activos - Planta de Carbonato de Litio"
APP_VERSION = "1.0.0"
ADMIN_EMAIL = "admin@control-activos.com"

# Configuración de IA
MIN_SAMPLES_IA = 10  # Número mínimo de muestras para usar modelos de IA
ZSCORE_THRESHOLD = 3.0  # Umbral para detección de anomalías
CLUSTERING_ITERATIONS = 10  # Número de iteraciones para K-means
RANDOM_FOREST_TREES = 100  # Número de árboles para Random Forest

# Configuración de criticidad
CRITICIDAD_WEIGHTS = {
    'impacto_produccion': 2.0,  # Peso del impacto en producción
    'disponibilidad_repuestos': 1.0,  # Peso de la disponibilidad de repuestos
    'probabilidad_falla': 1.5  # Peso de la probabilidad de falla
}

# Configuración de obsolescencia
ANOS_OBSOLESCENCIA_DEFAULT = 5  # Años por defecto para considerar obsoleto
VIDA_UTIL_DEFAULT = 10  # Vida útil por defecto en años
TIEMPO_RENOVACION_DEFAULT = 180  # Días por defecto para renovación (6 meses)

# Configuración de mantenimiento
INTERVALO_PREVENTIVO_DEFAULT = 90  # Días por defecto entre mantenimientos preventivos
ALERTA_MANTENIMIENTO_DIAS = 7  # Días de anticipación para alertar sobre mantenimientos

# Configuración de stock
CANTIDAD_MINIMA_DEFAULT = 1  # Cantidad mínima por defecto para stock
ALERTA_STOCK_BAJO = True  # Activar alertas de stock bajo

# Tipos de mantenimiento
TIPO_MANTENIMIENTO = {
    'PREVENTIVO': 'preventivo',
    'CORRECTIVO': 'correctivo',
    'PREDICTIVO': 'predictivo'
}

# Estados de mantenimiento
ESTADO_MANTENIMIENTO = {
    'PROGRAMADO': 'programado',
    'EN_PROCESO': 'en_proceso',
    'COMPLETADO': 'completado',
    'POSPUESTO': 'pospuesto',
    'CANCELADO': 'cancelado'
}

# Niveles de criticidad
NIVEL_CRITICIDAD = {
    'BAJA': 'baja',
    'MEDIA': 'media',
    'ALTA': 'alta',
    'EXTREMA': 'extrema'
}

# Niveles de impacto
NIVEL_IMPACTO = {
    'BAJO': 'bajo',
    'MEDIO': 'medio',
    'ALTO': 'alto',
    'CRITICO': 'critico'
}

# Configuración de archivos
ALLOWED_EXTENSIONS = {
    'excel': ['xlsx', 'xls'],
    'image': ['jpg', 'jpeg', 'png', 'gif'],
    'document': ['pdf', 'doc', 'docx']
}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

# Rutas de archivos
MODEL_PATH = 'media/models/'
ACTIVOS_IMAGES_PATH = 'media/activos/'

# Mensajes de sistema
MESSAGES = {
    'activo_created': 'Activo creado correctamente.',
    'activo_updated': 'Activo actualizado correctamente.',
    'activo_deleted': 'Activo eliminado correctamente.',
    'stock_updated': 'Stock actualizado correctamente.',
    'mantenimiento_created': 'Mantenimiento programado correctamente.',
    'mantenimiento_completed': 'Mantenimiento marcado como completado.',
    'error_ia': 'Error al procesar datos con inteligencia artificial.',
    'insufficient_data': 'Datos insuficientes para el análisis.'
}
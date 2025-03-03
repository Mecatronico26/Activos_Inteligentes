# utils/helpers.py
"""
Funciones auxiliares para el sistema de Control de Activos
"""

import os
import uuid
import datetime
from django.utils import timezone
from .constants import ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE

def generate_unique_filename(filename):
    """
    Genera un nombre de archivo único para evitar colisiones
    
    Args:
        filename (str): Nombre original del archivo
    
    Returns:
        str: Nombre de archivo único
    """
    ext = filename.split('.')[-1]
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return unique_name

def is_valid_file(file, allowed_types=None):
    """
    Verifica si un archivo es válido (extensión y tamaño)
    
    Args:
        file: Archivo a verificar
        allowed_types (list): Lista de tipos permitidos (default: None = todos)
    
    Returns:
        bool: True si el archivo es válido, False en caso contrario
    """
    if not file:
        return False
    
    # Verificar tamaño
    if file.size > MAX_UPLOAD_SIZE:
        return False
    
    # Verificar extensión
    if allowed_types:
        ext = file.name.split('.')[-1].lower()
        valid_extensions = []
        for type_key in allowed_types:
            if type_key in ALLOWED_EXTENSIONS:
                valid_extensions.extend(ALLOWED_EXTENSIONS[type_key])
        
        if ext not in valid_extensions:
            return False
    
    return True

def calculate_age_years(date):
    """
    Calcula la edad en años desde una fecha hasta hoy
    
    Args:
        date (date): Fecha de referencia
    
    Returns:
        int: Edad en años
    """
    if not date:
        return 0
    
    today = timezone.now().date()
    years = today.year - date.year
    
    # Ajustar si aún no ha pasado el aniversario de este año
    if today.month < date.month or (today.month == date.month and today.day < date.day):
        years -= 1
    
    return max(0, years)

def calculate_days_between(start_date, end_date=None):
    """
    Calcula los días entre dos fechas
    
    Args:
        start_date (date): Fecha de inicio
        end_date (date, optional): Fecha de fin (default: hoy)
    
    Returns:
        int: Número de días
    """
    if not start_date:
        return 0
    
    if not end_date:
        end_date = timezone.now().date()
    
    delta = end_date - start_date
    return delta.days

def format_currency(value):
    """
    Formatea un valor como moneda
    
    Args:
        value (float): Valor a formatear
    
    Returns:
        str: Valor formateado como moneda
    """
    if value is None:
        return "$0.00"
    
    return f"${value:,.2f}"

def get_month_name(month_number):
    """
    Obtiene el nombre del mes a partir de su número
    
    Args:
        month_number (int): Número del mes (1-12)
    
    Returns:
        str: Nombre del mes en español
    """
    months = [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ]
    
    if 1 <= month_number <= 12:
        return months[month_number - 1]
    
    return ""

def get_current_quarter():
    """
    Obtiene el trimestre actual
    
    Returns:
        tuple: (año, número de trimestre)
    """
    today = timezone.now().date()
    year = today.year
    month = today.month
    
    quarter = (month - 1) // 3 + 1
    
    return (year, quarter)

def get_quarter_date_range(year, quarter):
    """
    Obtiene el rango de fechas para un trimestre específico
    
    Args:
        year (int): Año
        quarter (int): Trimestre (1-4)
    
    Returns:
        tuple: (fecha_inicio, fecha_fin)
    """
    if quarter < 1 or quarter > 4:
        return None
    
    start_month = (quarter - 1) * 3 + 1
    
    start_date = datetime.date(year, start_month, 1)
    
    if quarter < 4:
        end_month = start_month + 3
        end_year = year
    else:
        end_month = 1
        end_year = year + 1
    
    end_date = datetime.date(end_year, end_month, 1) - datetime.timedelta(days=1)
    
    return (start_date, end_date)

def calculate_percentage(part, total):
    """
    Calcula un porcentaje
    
    Args:
        part (float): Parte
        total (float): Total
    
    Returns:
        float: Porcentaje (0-100)
    """
    if not total:
        return 0
    
    return round((part / total) * 100, 1)

def is_future_date(date):
    """
    Verifica si una fecha es en el futuro
    
    Args:
        date (date): Fecha a verificar
    
    Returns:
        bool: True si la fecha es en el futuro, False en caso contrario
    """
    return date > timezone.now().date()

def get_date_n_days_ago(days):
    """
    Obtiene la fecha hace n días
    
    Args:
        days (int): Número de días
    
    Returns:
        date: Fecha hace n días
    """
    return timezone.now().date() - datetime.timedelta(days=days)

def get_date_n_days_future(days):
    """
    Obtiene la fecha en n días
    
    Args:
        days (int): Número de días
    
    Returns:
        date: Fecha en n días
    """
    return timezone.now().date() + datetime.timedelta(days=days)
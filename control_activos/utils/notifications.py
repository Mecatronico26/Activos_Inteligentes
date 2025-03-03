# utils/notifications.py
"""
Sistema de notificaciones para el Control de Activos
"""

from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from .constants import ADMIN_EMAIL, APP_NAME
import logging

logger = logging.getLogger(__name__)

def send_email_notification(subject, message, recipient_list, html_message=None):
    """
    Envía una notificación por correo electrónico
    
    Args:
        subject (str): Asunto del correo
        message (str): Mensaje en texto plano
        recipient_list (list): Lista de destinatarios
        html_message (str, optional): Mensaje en formato HTML
    
    Returns:
        bool: True si el correo se envió correctamente, False en caso contrario
    """
    try:
        # Añadir prefijo al asunto
        subject = f"[{APP_NAME}] {subject}"
        
        # Enviar correo
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL or ADMIN_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False
        )
        
        logger.info(f"Correo enviado a {', '.join(recipient_list)}: {subject}")
        return True
    
    except Exception as e:
        logger.error(f"Error al enviar correo: {str(e)}")
        return False

def notify_stock_bajo(stock):
    """
    Notifica cuando un activo está en stock bajo
    
    Args:
        stock: Objeto StockActivo
    
    Returns:
        bool: True si la notificación se envió correctamente
    """
    # Obtener administradores
    admins = User.objects.filter(is_staff=True).values_list('email', flat=True)
    
    if not admins:
        logger.warning("No hay administradores para notificar sobre stock bajo")
        return False
    
    # Preparar mensajes
    subject = f"Stock bajo: {stock.nombre} ({stock.modelo})"
    
    # Mensaje de texto plano
    text_message = (
        f"ALERTA DE STOCK BAJO\n\n"
        f"El siguiente activo ha llegado a un nivel de stock bajo:\n\n"
        f"Nombre: {stock.nombre}\n"
        f"Modelo: {stock.modelo}\n"
        f"Fabricante: {stock.fabricante.nombre}\n"
        f"Cantidad actual: {stock.cantidad}\n"
        f"Cantidad mínima: {stock.cantidad_minima}\n\n"
        f"Por favor, revise y reabastezca el inventario según sea necesario.\n\n"
        f"Este es un mensaje automático, no responda a este correo."
    )
    
    # Mensaje HTML
    context = {
        'stock': stock,
        'fecha_actual': timezone.now()
    }
    html_message = render_to_string('emails/stock_bajo.html', context)
    
    # Enviar notificación
    return send_email_notification(subject, text_message, list(admins), html_message)

def notify_mantenimiento_proximo(mantenimiento, dias_faltantes):
    """
    Notifica sobre un mantenimiento próximo
    
    Args:
        mantenimiento: Objeto Mantenimiento
        dias_faltantes (int): Días faltantes para el mantenimiento
    
    Returns:
        bool: True si la notificación se envió correctamente
    """
    # Determinar destinatarios
    destinatarios = []
    
    # Añadir responsable si tiene correo
    if '@' in mantenimiento.responsable:
        destinatarios.append(mantenimiento.responsable)
    
    # Añadir administradores
    admins = User.objects.filter(is_staff=True).values_list('email', flat=True)
    destinatarios.extend(admins)
    
    if not destinatarios:
        logger.warning("No hay destinatarios para notificar sobre mantenimiento próximo")
        return False
    
    # Preparar mensajes
    subject = f"Mantenimiento próximo: {mantenimiento.nombre} en {dias_faltantes} días"
    
    # Mensaje de texto plano
    text_message = (
        f"RECORDATORIO DE MANTENIMIENTO\n\n"
        f"Se aproxima un mantenimiento programado:\n\n"
        f"Activo: {mantenimiento.nombre} - {mantenimiento.modelo}\n"
        f"Tipo: {mantenimiento.get_tipo_display()}\n"
        f"Fecha programada: {mantenimiento.fecha_programada.strftime('%d/%m/%Y')}\n"
        f"Días faltantes: {dias_faltantes}\n"
        f"Responsable: {mantenimiento.responsable}\n\n"
        f"Acciones a realizar: {mantenimiento.acciones}\n\n"
        f"Este es un mensaje automático, no responda a este correo."
    )
    
    # Mensaje HTML
    context = {
        'mantenimiento': mantenimiento,
        'dias_faltantes': dias_faltantes,
        'fecha_actual': timezone.now()
    }
    html_message = render_to_string('emails/mantenimiento_proximo.html', context)
    
    # Enviar notificación
    return send_email_notification(subject, text_message, list(set(destinatarios)), html_message)

def notify_anomalia_detectada(lectura):
    """
    Notifica cuando se detecta una anomalía en una lectura
    
    Args:
        lectura: Objeto LecturaPredictiva
    
    Returns:
        bool: True si la notificación se envió correctamente
    """
    # Obtener administradores y responsables
    destinatarios = []
    
    # Añadir responsable de la lectura
    if '@' in lectura.responsable:
        destinatarios.append(lectura.responsable)
    
    # Añadir administradores
    admins = User.objects.filter(is_staff=True).values_list('email', flat=True)
    destinatarios.extend(admins)
    
    if not destinatarios:
        logger.warning("No hay destinatarios para notificar sobre anomalía detectada")
        return False
    
    # Preparar mensajes
    subject = f"ALERTA: Anomalía detectada en {lectura.plan.activo.nombre if lectura.plan.activo else 'activo'}"
    
    # Mensaje de texto plano
    text_message = (
        f"ALERTA DE ANOMALÍA DETECTADA\n\n"
        f"Se ha detectado una lectura anómala:\n\n"
        f"Plan: {lectura.plan.nombre_plan}\n"
        f"Activo: {lectura.plan.activo.nombre if lectura.plan.activo else 'No especificado'}\n"
        f"Parámetro: {lectura.plan.parametros_medicion}\n"
        f"Valor medido: {lectura.valor_medido} {lectura.plan.unidad_medida}\n"
        f"Valor umbral: {lectura.plan.valor_umbral} {lectura.plan.unidad_medida}\n"
        f"Fecha de lectura: {lectura.fecha_lectura.strftime('%d/%m/%Y %H:%M')}\n"
        f"Responsable: {lectura.responsable}\n\n"
        f"Se recomienda revisar el activo y programar un mantenimiento correctivo si es necesario.\n\n"
        f"Este es un mensaje automático, no responda a este correo."
    )
    
    # Mensaje HTML
    context = {
        'lectura': lectura,
        'fecha_actual': timezone.now()
    }
    html_message = render_to_string('emails/anomalia_detectada.html', context)
    
    # Enviar notificación
    return send_email_notification(subject, text_message, list(set(destinatarios)), html_message)

def notify_activo_obsoleto(activo_obsoleto):
    """
    Notifica cuando un activo se considera obsoleto
    
    Args:
        activo_obsoleto: Objeto ActivoObsoleto
    
    Returns:
        bool: True si la notificación se envió correctamente
    """
    # Obtener administradores
    admins = User.objects.filter(is_staff=True).values_list('email', flat=True)
    
    if not admins:
        logger.warning("No hay administradores para notificar sobre activo obsoleto")
        return False
    
    # Preparar mensajes
    subject = f"Activo obsoleto: {activo_obsoleto.nombre} requiere atención"
    
    # Mensaje de texto plano
    anos_servicio = activo_obsoleto.anos_en_servicio()
    vida_util = activo_obsoleto.vida_util
    porcentaje = activo_obsoleto.porcentaje_vida_util_consumida()
    
    text_message = (
        f"NOTIFICACIÓN DE ACTIVO OBSOLETO\n\n"
        f"El siguiente activo ha sido identificado como obsoleto:\n\n"
        f"Nombre: {activo_obsoleto.nombre}\n"
        f"Modelo: {activo_obsoleto.modelo}\n"
        f"Fabricante: {activo_obsoleto.fabricante.nombre}\n"
        f"Año de instalación: {activo_obsoleto.ano_instalacion}\n"
        f"Años en servicio: {anos_servicio}\n"
        f"Vida útil: {vida_util}\n"
        f"Porcentaje consumido: {porcentaje}%\n"
        f"Estado actual: {activo_obsoleto.get_estado_actual_display()}\n"
        f"Disponibilidad de repuestos: {activo_obsoleto.get_disponibilidad_repuestos_display()}\n\n"
        f"Estrategia de mitigación: {activo_obsoleto.get_estrategia_mitigacion_display()}\n"
        f"Fecha de renovación: {activo_obsoleto.fecha_renovacion.strftime('%d/%m/%Y') if activo_obsoleto.fecha_renovacion else 'No establecida'}\n"
        f"Presupuesto estimado: ${activo_obsoleto.presupuesto_estimado if activo_obsoleto.presupuesto_estimado else 'No especificado'}\n\n"
        f"Se recomienda revisar y actualizar el plan de renovación para este activo.\n\n"
        f"Este es un mensaje automático, no responda a este correo."
    )
    
    # Mensaje HTML
    context = {
        'activo_obsoleto': activo_obsoleto,
        'anos_servicio': anos_servicio,
        'porcentaje': porcentaje,
        'fecha_actual': timezone.now()
    }
    html_message = render_to_string('emails/activo_obsoleto.html', context)
    
    # Enviar notificación
    return send_email_notification(subject, text_message, list(admins), html_message)
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()


class Alert(models.Model):
    """Modelo para alertas y recordatorios del sistema"""
    
    ALERT_TYPES = [
        ('reminder', 'Recordatorio'),
        ('notification', 'Notificación'),
        ('warning', 'Advertencia'),
        ('info', 'Información'),
        ('success', 'Éxito'),
        ('error', 'Error'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('read', 'Leída'),
        ('dismissed', 'Descartada'),
        ('expired', 'Expirada'),
    ]
    
    FREQUENCY_CHOICES = [
        ('once', 'Una vez'),
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('yearly', 'Anual'),
    ]
    
    # Información básica
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensaje")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES, default='info', verbose_name="Tipo de alerta")
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium', verbose_name="Prioridad")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Estado")
    
    # Usuario y destinatarios
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts', verbose_name="Usuario")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_alerts', verbose_name="Creado por")
    
    # Configuración de tiempo
    scheduled_at = models.DateTimeField(verbose_name="Programada para")
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name="Expira en")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once', verbose_name="Frecuencia")
    
    # Metadatos
    icon = models.CharField(max_length=50, default='bell', verbose_name="Icono")
    color = models.CharField(max_length=20, default='primary', verbose_name="Color")
    action_url = models.URLField(blank=True, null=True, verbose_name="URL de acción")
    action_text = models.CharField(max_length=100, blank=True, verbose_name="Texto de acción")
    
    # Configuración
    is_recurring = models.BooleanField(default=False, verbose_name="Es recurrente")
    is_system_alert = models.BooleanField(default=False, verbose_name="Alerta del sistema")
    send_email = models.BooleanField(default=False, verbose_name="Enviar por email")
    send_push = models.BooleanField(default=True, verbose_name="Enviar notificación push")
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Leído en")
    dismissed_at = models.DateTimeField(null=True, blank=True, verbose_name="Descartado en")
    
    class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Marca la alerta como leída"""
        self.status = 'read'
        self.read_at = timezone.now()
        self.save()
    
    def dismiss(self):
        """Descarta la alerta"""
        self.status = 'dismissed'
        self.dismissed_at = timezone.now()
        self.save()
    
    def is_expired(self):
        """Verifica si la alerta ha expirado"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def time_until_scheduled(self):
        """Tiempo hasta que se active la alerta"""
        if self.scheduled_at > timezone.now():
            return self.scheduled_at - timezone.now()
        return timedelta(0)
    
    def get_priority_color(self):
        """Retorna el color según la prioridad"""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545'
        }
        return colors.get(self.priority, '#6c757d')
    
    def get_type_icon(self):
        """Retorna el icono según el tipo"""
        icons = {
            'reminder': 'clock',
            'notification': 'bell',
            'warning': 'exclamation-triangle',
            'info': 'info-circle',
            'success': 'check-circle',
            'error': 'times-circle'
        }
        return icons.get(self.alert_type, 'bell')
    
    @classmethod
    def generate_mock_alerts(cls, user, count=10):
        """Genera alertas mock para pruebas"""
        alerts = []
        
        mock_data = [
            {
                'title': 'Reunión con cliente',
                'message': 'Tienes una reunión programada con el cliente en 30 minutos',
                'alert_type': 'reminder',
                'priority': 'high'
            },
            {
                'title': 'Nuevo lead asignado',
                'message': 'Se te ha asignado un nuevo lead para seguimiento',
                'alert_type': 'notification',
                'priority': 'medium'
            },
            {
                'title': 'Contrato por vencer',
                'message': 'El contrato #12345 vence en 3 días',
                'alert_type': 'warning',
                'priority': 'high'
            },
            {
                'title': 'Pago recibido',
                'message': 'Se ha recibido el pago de $50,000 del cliente ABC',
                'alert_type': 'success',
                'priority': 'medium'
            },
            {
                'title': 'Error en el sistema',
                'message': 'Se detectó un error en el módulo de reportes',
                'alert_type': 'error',
                'priority': 'urgent'
            },
            {
                'title': 'Actualización disponible',
                'message': 'Hay una nueva versión del sistema disponible',
                'alert_type': 'info',
                'priority': 'low'
            },
            {
                'title': 'Seguimiento pendiente',
                'message': 'Tienes 5 leads pendientes de seguimiento',
                'alert_type': 'reminder',
                'priority': 'medium'
            },
            {
                'title': 'Meta alcanzada',
                'message': '¡Felicidades! Has alcanzado tu meta mensual de ventas',
                'alert_type': 'success',
                'priority': 'medium'
            }
        ]
        
        for i in range(count):
            data = random.choice(mock_data)
            
            # Fechas aleatorias
            now = timezone.now()
            scheduled_at = now + timedelta(
                hours=random.randint(-24, 72),
                minutes=random.randint(0, 59)
            )
            
            alert = cls.objects.create(
                title=data['title'],
                message=data['message'],
                alert_type=data['alert_type'],
                priority=data['priority'],
                status=random.choice(['active', 'read', 'dismissed']),
                user=user,
                created_by=user,
                scheduled_at=scheduled_at,
                expires_at=scheduled_at + timedelta(days=random.randint(1, 30)),
                frequency=random.choice(['once', 'daily', 'weekly']),
                is_recurring=random.choice([True, False]),
                send_email=random.choice([True, False]),
                send_push=True
            )
            alerts.append(alert)
        
        return alerts


class AlertTemplate(models.Model):
    """Plantillas para alertas recurrentes"""
    
    name = models.CharField(max_length=200, verbose_name="Nombre de la plantilla")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Configuración de la alerta
    title_template = models.CharField(max_length=200, verbose_name="Plantilla del título")
    message_template = models.TextField(verbose_name="Plantilla del mensaje")
    alert_type = models.CharField(max_length=20, choices=Alert.ALERT_TYPES, default='reminder', verbose_name="Tipo de alerta")
    priority = models.CharField(max_length=10, choices=Alert.PRIORITY_LEVELS, default='medium', verbose_name="Prioridad")
    
    # Configuración de tiempo
    frequency = models.CharField(max_length=20, choices=Alert.FREQUENCY_CHOICES, default='weekly', verbose_name="Frecuencia")
    advance_time = models.DurationField(default=timedelta(hours=1), verbose_name="Tiempo de anticipación")
    
    # Metadatos
    icon = models.CharField(max_length=50, default='bell', verbose_name="Icono")
    color = models.CharField(max_length=20, default='primary', verbose_name="Color")
    
    # Estado
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Creado por")
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")
    
    class Meta:
        verbose_name = "Plantilla de Alerta"
        verbose_name_plural = "Plantillas de Alertas"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class AlertRule(models.Model):
    """Reglas automáticas para generar alertas"""
    
    TRIGGER_TYPES = [
        ('date_based', 'Basada en fecha'),
        ('event_based', 'Basada en evento'),
        ('condition_based', 'Basada en condición'),
        ('time_based', 'Basada en tiempo'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Nombre de la regla")
    description = models.TextField(blank=True, verbose_name="Descripción")
    
    # Configuración del disparador
    trigger_type = models.CharField(max_length=20, choices=TRIGGER_TYPES, verbose_name="Tipo de disparador")
    trigger_condition = models.JSONField(default=dict, verbose_name="Condición del disparador")
    
    # Plantilla asociada
    template = models.ForeignKey(AlertTemplate, on_delete=models.CASCADE, verbose_name="Plantilla")
    
    # Configuración
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    target_users = models.ManyToManyField(User, blank=True, verbose_name="Usuarios objetivo")
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Actualizado en")
    last_triggered = models.DateTimeField(null=True, blank=True, verbose_name="Último disparo")
    
    class Meta:
        verbose_name = "Regla de Alerta"
        verbose_name_plural = "Reglas de Alertas"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class AlertLog(models.Model):
    """Log de alertas enviadas"""
    
    DELIVERY_STATUS = [
        ('pending', 'Pendiente'),
        ('sent', 'Enviada'),
        ('delivered', 'Entregada'),
        ('failed', 'Fallida'),
        ('read', 'Leída'),
    ]
    
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='logs', verbose_name="Alerta")
    status = models.CharField(max_length=20, choices=DELIVERY_STATUS, default='pending', verbose_name="Estado")
    
    # Detalles del envío
    delivery_method = models.CharField(max_length=50, verbose_name="Método de entrega")  # email, push, sms, etc.
    recipient = models.CharField(max_length=200, verbose_name="Destinatario")
    
    # Metadatos
    sent_at = models.DateTimeField(null=True, blank=True, verbose_name="Enviado en")
    delivered_at = models.DateTimeField(null=True, blank=True, verbose_name="Entregado en")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Leído en")
    
    # Información adicional
    error_message = models.TextField(blank=True, verbose_name="Mensaje de error")
    metadata = models.JSONField(default=dict, verbose_name="Metadatos")
    
    # Fechas
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Creado en")
    
    class Meta:
        verbose_name = "Log de Alerta"
        verbose_name_plural = "Logs de Alertas"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert.title} - {self.status}"

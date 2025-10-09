from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Activity(models.Model):
    """
    Modelo para gestionar las actividades de los agentes inmobiliarios.
    Permite crear, listar y gestionar tareas con diferentes tipos y estados.
    """
    
    ACTIVITY_TYPES = [
        ('llamada', 'Llamada telefónica'),
        ('reunion', 'Reunión'),
        ('visita', 'Visita a propiedad'),
        ('seguimiento', 'Seguimiento de cliente'),
        ('documentacion', 'Gestión de documentos'),
        ('marketing', 'Actividad de marketing'),
        ('prospección', 'Prospección de clientes'),
        ('otro', 'Otro'),
    ]
    
    ACTIVITY_STATUS = [
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('pospuesta', 'Pospuesta'),
    ]
    
    PRIORITY_LEVELS = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]
    
    # Campos principales
    titulo = models.CharField(max_length=200, help_text="Título descriptivo de la actividad")
    descripcion = models.TextField(blank=True, help_text="Descripción detallada de la actividad")
    tipo = models.CharField(max_length=20, choices=ACTIVITY_TYPES, default='otro')
    estado = models.CharField(max_length=20, choices=ACTIVITY_STATUS, default='pendiente')
    prioridad = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='media')
    
    # Fechas y tiempos
    fecha_programada = models.DateTimeField(help_text="Fecha y hora programada para la actividad")
    fecha_vencimiento = models.DateTimeField(null=True, blank=True, help_text="Fecha límite para completar")
    fecha_completada = models.DateTimeField(null=True, blank=True)
    
    # Relaciones
    asignado_a = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='actividades_asignadas',
        help_text="Usuario responsable de la actividad"
    )
    creado_por = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='actividades_creadas',
        help_text="Usuario que creó la actividad"
    )
    
    # Metadatos
    notas = models.TextField(blank=True, help_text="Notas adicionales o comentarios")
    ubicacion = models.CharField(max_length=300, blank=True, help_text="Ubicación donde se realizará la actividad")
    duracion_estimada = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        help_text="Duración estimada en minutos"
    )
    
    # Campos de auditoría
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Actividad"
        verbose_name_plural = "Actividades"
        ordering = ['-fecha_programada', '-prioridad']
        indexes = [
            models.Index(fields=['estado', 'fecha_programada']),
            models.Index(fields=['asignado_a', 'estado']),
            models.Index(fields=['tipo', 'estado']),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.get_estado_display()}"
    
    @property
    def is_overdue(self):
        """Verifica si la actividad está vencida"""
        if self.fecha_vencimiento and self.estado in ['pendiente', 'en_progreso']:
            return timezone.now() > self.fecha_vencimiento
        return False
    
    @property
    def is_today(self):
        """Verifica si la actividad está programada para hoy"""
        today = timezone.now().date()
        return self.fecha_programada.date() == today
    
    def marcar_completada(self):
        """Marca la actividad como completada"""
        self.estado = 'completada'
        self.fecha_completada = timezone.now()
        self.save()
    
    def get_priority_color(self):
        """Retorna un color asociado a la prioridad"""
        colors = {
            'baja': '#28a745',      # Verde
            'media': '#ffc107',     # Amarillo
            'alta': '#fd7e14',      # Naranja
            'urgente': '#dc3545',   # Rojo
        }
        return colors.get(self.prioridad, '#6c757d')
    
    def get_status_color(self):
        """Retorna un color asociado al estado"""
        colors = {
            'pendiente': '#6c757d',     # Gris
            'en_progreso': '#007bff',   # Azul
            'completada': '#28a745',    # Verde
            'cancelada': '#dc3545',     # Rojo
            'pospuesta': '#ffc107',     # Amarillo
        }
        return colors.get(self.estado, '#6c757d')

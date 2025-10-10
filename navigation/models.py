from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class MenuSection(models.Model):
    """
    Modelo para las secciones del menú de navegación
    """
    SECTION_TYPES = [
        ('dashboard', 'Dashboard'),
        ('properties', 'Propiedades'),
        ('clients', 'Clientes'),
        ('activities', 'Actividades'),
        ('reports', 'Reportes'),
        ('contracts', 'Contratos'),
        ('messages', 'Mensajería'),
        ('alerts', 'Alertas'),
        ('networks', 'Redes'),
        ('settings', 'Configuración'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(unique=True, verbose_name="Slug")
    icon = models.CharField(max_length=50, verbose_name="Icono", help_text="Clase CSS del icono")
    url = models.CharField(max_length=200, verbose_name="URL")
    section_type = models.CharField(max_length=20, choices=SECTION_TYPES, verbose_name="Tipo de Sección")
    order = models.PositiveIntegerField(default=0, verbose_name="Orden")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    requires_permission = models.CharField(max_length=100, blank=True, null=True, verbose_name="Permiso Requerido")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, verbose_name="Sección Padre")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Sección del Menú"
        verbose_name_plural = "Secciones del Menú"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class UserNavigation(models.Model):
    """
    Modelo para rastrear la navegación del usuario y sección activa
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    current_section = models.ForeignKey(MenuSection, on_delete=models.CASCADE, verbose_name="Sección Actual")
    last_accessed = models.DateTimeField(auto_now=True, verbose_name="Último Acceso")
    
    class Meta:
        verbose_name = "Navegación del Usuario"
        verbose_name_plural = "Navegación de Usuarios"
        unique_together = ['user']
    
    def __str__(self):
        return f"{self.user.email} - {self.current_section.name}"


class Notification(models.Model):
    """
    Modelo para notificaciones básicas del sistema
    """
    NOTIFICATION_TYPES = [
        ('info', 'Información'),
        ('success', 'Éxito'),
        ('warning', 'Advertencia'),
        ('error', 'Error'),
        ('activity', 'Actividad'),
        ('message', 'Mensaje'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Usuario")
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensaje")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='info', verbose_name="Tipo")
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium', verbose_name="Prioridad")
    is_read = models.BooleanField(default=False, verbose_name="Leída")
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    action_url = models.CharField(max_length=200, blank=True, null=True, verbose_name="URL de Acción")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    read_at = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de Lectura")
    
    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.email}"
    
    def mark_as_read(self):
        """Marcar notificación como leída"""
        from django.utils import timezone
        self.is_read = True
        self.read_at = timezone.now()
        self.save()

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Alert, AlertTemplate, AlertRule, AlertLog


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'alert_type', 'priority_badge', 'status_badge', 'user', 
        'scheduled_at', 'expires_at', 'days_since_created', 'created_at', 'status', 'priority'
    ]
    list_filter = ['alert_type', 'priority', 'status', 'created_at', 'scheduled_at']
    search_fields = ['title', 'message', 'user__username', 'user__email', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'days_since_created']
    list_editable = ['status', 'priority']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Información de la Alerta', {
            'fields': ('title', 'message', 'alert_type', 'priority')
        }),
        ('Destinatario', {
            'fields': ('user', 'created_by')
        }),
        ('Programación', {
            'fields': ('scheduled_at', 'expires_at', 'frequency', 'recurrence_end')
        }),
        ('Estado', {
            'fields': ('status', 'is_read')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at', 'days_since_created'),
            'classes': ('collapse',)
        })
    )
    
    def priority_badge(self, obj):
        """Muestra un badge con el color de la prioridad"""
        colors = {
            'low': 'success',
            'medium': 'warning', 
            'high': 'danger',
            'urgent': 'dark'
        }
        color = colors.get(obj.priority, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Prioridad'
    
    def status_badge(self, obj):
        """Muestra un badge con el estado de la alerta"""
        colors = {
            'pending': 'warning',
            'sent': 'success',
            'read': 'info',
            'dismissed': 'secondary',
            'expired': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def days_since_created(self, obj):
        """Calcula los días desde la creación"""
        delta = timezone.now() - obj.created_at
        days = delta.days
        if days == 0:
            return "Hoy"
        elif days == 1:
            return "Ayer"
        else:
            return f"Hace {days} días"
    days_since_created.short_description = 'Antigüedad'
    
    actions = ['mark_as_read', 'mark_as_dismissed', 'mark_as_sent', 'delete_selected']
    
    def mark_as_read(self, request, queryset):
        """Marca las alertas seleccionadas como leídas"""
        updated = queryset.update(status='read', is_read=True)
        self.message_user(request, f'{updated} alertas marcadas como leídas.')
    mark_as_read.short_description = 'Marcar como leídas'
    
    def mark_as_dismissed(self, request, queryset):
        """Marca las alertas seleccionadas como descartadas"""
        updated = queryset.update(status='dismissed')
        self.message_user(request, f'{updated} alertas descartadas.')
    mark_as_dismissed.short_description = 'Descartar alertas'
    
    def mark_as_sent(self, request, queryset):
        """Marca las alertas seleccionadas como enviadas"""
        updated = queryset.update(status='sent')
        self.message_user(request, f'{updated} alertas marcadas como enviadas.')
    mark_as_sent.short_description = 'Marcar como enviadas'


@admin.register(AlertTemplate)
class AlertTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'alert_type', 'priority', 'is_active', 'usage_count', 'created_by', 'created_at'
    ]
    list_filter = ['alert_type', 'priority', 'is_active', 'created_at']
    search_fields = ['name', 'title_template', 'message_template', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'usage_count']
    list_editable = ['is_active', 'priority']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información de la Plantilla', {
            'fields': ('name', 'alert_type', 'priority', 'is_active')
        }),
        ('Plantillas de Contenido', {
            'fields': ('title_template', 'message_template')
        }),
        ('Configuración', {
            'fields': ('default_frequency', 'created_by')
        }),
        ('Estadísticas', {
            'fields': ('usage_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def usage_count(self, obj):
        """Cuenta cuántas alertas usan esta plantilla"""
        return obj.alerts.count()
    usage_count.short_description = 'Usos'
    
    actions = ['activate_templates', 'deactivate_templates']
    
    def activate_templates(self, request, queryset):
        """Activa las plantillas seleccionadas"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} plantillas activadas.')
    activate_templates.short_description = 'Activar plantillas'
    
    def deactivate_templates(self, request, queryset):
        """Desactiva las plantillas seleccionadas"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} plantillas desactivadas.')
    deactivate_templates.short_description = 'Desactivar plantillas'


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'trigger_type', 'template', 'is_active', 'last_triggered', 'created_at'
    ]
    list_filter = ['trigger_type', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'template__name', 'created_by__username']
    readonly_fields = ['created_at', 'updated_at', 'execution_count']
    list_editable = ['is_active']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información de la Regla', {
            'fields': ('name', 'description', 'trigger_type', 'is_active')
        }),
        ('Configuración', {
            'fields': ('template', 'conditions', 'target_users')
        }),
        ('Estadísticas', {
            'fields': ('execution_count', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def execution_count(self, obj):
        """Cuenta cuántas veces se ha ejecutado esta regla"""
        return obj.alert_logs.count()
    execution_count.short_description = 'Ejecuciones'
    
    actions = ['activate_rules', 'deactivate_rules']
    
    def activate_rules(self, request, queryset):
        """Activa las reglas seleccionadas"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} reglas activadas.')
    activate_rules.short_description = 'Activar reglas'
    
    def deactivate_rules(self, request, queryset):
        """Desactiva las reglas seleccionadas"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} reglas desactivadas.')
    deactivate_rules.short_description = 'Desactivar reglas'


@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display = [
        'alert', 'delivery_method', 'status_badge', 'sent_at', 'error_message_short', 'created_at'
    ]
    list_filter = ['delivery_method', 'status', 'sent_at', 'created_at']
    search_fields = ['alert__title', 'alert__user__username', 'error_message']
    readonly_fields = ['created_at', 'sent_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Log', {
            'fields': ('alert', 'delivery_method', 'status')
        }),
        ('Detalles de Entrega', {
            'fields': ('sent_at', 'error_message')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        """Muestra un badge con el estado del log"""
        colors = {
            'pending': 'warning',
            'sent': 'success',
            'failed': 'danger',
            'retry': 'info'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def error_message_short(self, obj):
        """Muestra una versión corta del mensaje de error"""
        if obj.error_message:
            return obj.error_message[:50] + '...' if len(obj.error_message) > 50 else obj.error_message
        return '-'
    error_message_short.short_description = 'Error'
    
    actions = ['retry_failed_deliveries']
    
    def retry_failed_deliveries(self, request, queryset):
        """Reintenta las entregas fallidas"""
        failed_logs = queryset.filter(status='failed')
        updated = failed_logs.update(status='retry')
        self.message_user(request, f'{updated} entregas marcadas para reintento.')
    retry_failed_deliveries.short_description = 'Reintentar entregas fallidas'

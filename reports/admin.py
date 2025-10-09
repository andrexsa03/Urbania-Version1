from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Report, ReportChart, ReportData, ReportSubscription


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'report_type', 'status_badge', 'status', 'period', 'total_records',
        'file_size', 'created_by', 'is_public', 'days_since_created', 'created_at'
    ]
    list_filter = ['report_type', 'status', 'period', 'is_public', 'created_at', 'created_by']
    search_fields = ['name', 'description', 'created_by__username', 'created_by__email']
    readonly_fields = ['created_at', 'updated_at', 'days_since_created']
    list_editable = ['is_public', 'status']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Información del Reporte', {
            'fields': ('name', 'description', 'report_type', 'period')
        }),
        ('Configuración', {
            'fields': ('start_date', 'end_date', 'is_public', 'expires_at')
        }),
        ('Estado y Datos', {
            'fields': ('status', 'total_records', 'file_size', 'file_path')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        """Muestra el estado con badge colorido"""
        color_map = {
            'pending': 'warning',
            'processing': 'info',
            'ready': 'success',
            'error': 'danger',
            'expired': 'secondary'
        }
        color = color_map.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def days_since_created(self, obj):
        """Muestra los días desde la creación"""
        days = (timezone.now().date() - obj.created_at.date()).days
        if days == 0:
            return "Hoy"
        elif days == 1:
            return "Ayer"
        else:
            return f"Hace {days} días"
    days_since_created.short_description = 'Antigüedad'
    
    def status_color(self, obj):
        """Muestra el color del estado"""
        color_map = {
            'pending': '#ffc107',
            'processing': '#17a2b8',
            'ready': '#28a745',
            'error': '#dc3545',
            'expired': '#6c757d'
        }
        color = color_map.get(obj.status, '#6c757d')
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border-radius: 3px;"></div>',
            color
        )
    status_color.short_description = 'Color Estado'
    
    actions = ['mark_as_ready', 'mark_as_expired', 'make_public', 'make_private']
    
    def mark_as_ready(self, request, queryset):
        """Marca los reportes como listos"""
        updated = queryset.update(status='ready')
        self.message_user(request, f'{updated} reportes marcados como listos.')
    mark_as_ready.short_description = 'Marcar como listos'
    
    def mark_as_expired(self, request, queryset):
        """Marca los reportes como expirados"""
        updated = queryset.update(status='expired')
        self.message_user(request, f'{updated} reportes marcados como expirados.')
    mark_as_expired.short_description = 'Marcar como expirados'
    
    def make_public(self, request, queryset):
        """Hace públicos los reportes seleccionados"""
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} reportes marcados como públicos.')
    make_public.short_description = 'Hacer públicos'
    
    def make_private(self, request, queryset):
        """Hace privados los reportes seleccionados"""
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} reportes marcados como privados.')
    make_private.short_description = 'Hacer privados'


@admin.register(ReportChart)
class ReportChartAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'report', 'chart_type', 'data_count', 'color_preview',
        'is_active', 'order', 'created_at'
    ]
    list_filter = ['chart_type', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'report__name']
    readonly_fields = ['created_at', 'data_count']
    list_editable = ['is_active', 'order']
    ordering = ['report', 'order']
    
    fieldsets = (
        ('Información del Gráfico', {
            'fields': ('report', 'title', 'description', 'chart_type')
        }),
        ('Configuración de Ejes', {
            'fields': ('x_axis_label', 'y_axis_label')
        }),
        ('Presentación', {
            'fields': ('color', 'order', 'is_active')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'data_count'),
            'classes': ('collapse',)
        })
    )
    
    def data_count(self, obj):
        """Cuenta los datos del gráfico"""
        return obj.data.count()
    data_count.short_description = 'Datos'
    
    def color_preview(self, obj):
        """Muestra una vista previa del color"""
        if obj.color:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
                obj.color
            )
        return '-'
    color_preview.short_description = 'Color'
    
    actions = ['activate_charts', 'deactivate_charts']
    
    def activate_charts(self, request, queryset):
        """Activa los gráficos seleccionados"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} gráficos activados.')
    activate_charts.short_description = 'Activar gráficos'
    
    def deactivate_charts(self, request, queryset):
        """Desactiva los gráficos seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} gráficos desactivados.')
    deactivate_charts.short_description = 'Desactivar gráficos'


@admin.register(ReportData)
class ReportDataAdmin(admin.ModelAdmin):
    list_display = [
        'chart', 'label', 'formatted_value', 'color_preview', 'order'
    ]
    list_filter = ['chart__chart_type', 'chart__report__report_type']
    search_fields = ['label', 'chart__title', 'chart__report__name']
    readonly_fields = ['formatted_value']
    list_editable = ['order']
    ordering = ['chart', 'order']
    
    fieldsets = (
        ('Información del Dato', {
            'fields': ('chart', 'label', 'value')
        }),
        ('Presentación', {
            'fields': ('color', 'order')
        }),
        ('Metadatos', {
            'fields': ('formatted_value',),
            'classes': ('collapse',)
        })
    )
    
    def formatted_value(self, obj):
        """Muestra el valor formateado"""
        if obj.value >= 1000000:
            return f"{obj.value/1000000:.1f}M"
        elif obj.value >= 1000:
            return f"{obj.value/1000:.1f}K"
        else:
            return str(obj.value)
    formatted_value.short_description = 'Valor'
    
    def color_preview(self, obj):
        """Muestra una vista previa del color"""
        if obj.color:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
                obj.color
            )
        return '-'
    color_preview.short_description = 'Color'


@admin.register(ReportSubscription)
class ReportSubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'report_type', 'frequency', 'is_active', 'last_sent',
        'next_send_date', 'created_at'
    ]
    list_filter = ['frequency', 'is_active', 'created_at', 'last_sent']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'last_sent', 'next_send_date']
    list_editable = ['is_active']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información de la Suscripción', {
            'fields': ('user', 'report_type', 'frequency')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'last_sent', 'next_send_date'),
            'classes': ('collapse',)
        })
    )
    
    def next_send_date(self, obj):
        """Calcula la próxima fecha de envío"""
        if not obj.last_sent:
            return "Pendiente primer envío"
        
        from datetime import timedelta
        
        frequency_days = {
            'daily': 1,
            'weekly': 7,
            'monthly': 30,
            'quarterly': 90
        }
        
        days = frequency_days.get(obj.frequency, 7)
        next_date = obj.last_sent + timedelta(days=days)
        
        if next_date.date() <= timezone.now().date():
            return format_html('<span style="color: red;">Vencido</span>')
        else:
            return next_date.strftime('%d/%m/%Y')
    
    next_send_date.short_description = 'Próximo Envío'
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        """Activa las suscripciones seleccionadas"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} suscripciones activadas.')
    activate_subscriptions.short_description = 'Activar suscripciones'
    
    def deactivate_subscriptions(self, request, queryset):
        """Desactiva las suscripciones seleccionadas"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} suscripciones desactivadas.')
    deactivate_subscriptions.short_description = 'Desactivar suscripciones'

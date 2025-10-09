from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import DashboardMetric, ChartData, RecentActivity


@admin.register(DashboardMetric)
class DashboardMetricAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'metric_type', 'formatted_value', 'percentage_change_badge',
        'trend_badge', 'is_active', 'updated_at'
    ]
    list_filter = ['metric_type', 'is_active', 'color', 'created_at']
    search_fields = ['name', 'metric_type']
    readonly_fields = ['percentage_change', 'created_at', 'updated_at']
    list_editable = ['is_active']
    ordering = ['metric_type', 'name']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'metric_type', 'icon', 'color')
        }),
        ('Valores', {
            'fields': ('value', 'previous_value', 'percentage_change')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def formatted_value(self, obj):
        """Muestra el valor formateado"""
        if obj.metric_type == 'monthly_revenue':
            return f"${obj.value:,.0f}"
        return f"{obj.value:,.0f}"
    formatted_value.short_description = 'Valor'
    
    def percentage_change_badge(self, obj):
        """Muestra el cambio porcentual con badge"""
        if obj.percentage_change is None:
            return format_html('<span class="badge badge-secondary">N/A</span>')
        
        color = 'success' if obj.percentage_change > 0 else 'danger' if obj.percentage_change < 0 else 'warning'
        symbol = '+' if obj.percentage_change > 0 else ''
        
        return format_html(
            '<span class="badge badge-{}">{}{:.1f}%</span>',
            color, symbol, obj.percentage_change
        )
    percentage_change_badge.short_description = 'Cambio %'
    
    def trend_badge(self, obj):
        """Muestra la tendencia con badge de color"""
        color = obj.get_trend_color()
        color_map = {
            'success': '🟢',
            'danger': '🔴',
            'warning': '🟡',
            'secondary': '⚪'
        }
        return format_html(
            '<span title="{}">{}</span>',
            color, color_map.get(color, '⚪')
        )
    trend_badge.short_description = 'Tendencia'
    
    actions = ['activate_metrics', 'deactivate_metrics', 'calculate_percentage_changes']
    
    def activate_metrics(self, request, queryset):
        """Activa las métricas seleccionadas"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} métricas activadas.')
    activate_metrics.short_description = 'Activar métricas seleccionadas'
    
    def deactivate_metrics(self, request, queryset):
        """Desactiva las métricas seleccionadas"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} métricas desactivadas.')
    deactivate_metrics.short_description = 'Desactivar métricas seleccionadas'
    
    def calculate_percentage_changes(self, request, queryset):
        """Recalcula los cambios porcentuales"""
        count = 0
        for metric in queryset:
            metric.calculate_percentage_change()
            metric.save()
            count += 1
        self.message_user(request, f'Cambios porcentuales recalculados para {count} métricas.')
    calculate_percentage_changes.short_description = 'Recalcular cambios porcentuales'


@admin.register(ChartData)
class ChartDataAdmin(admin.ModelAdmin):
    list_display = [
        'chart_name', 'chart_type', 'label', 'formatted_value',
        'color_preview', 'date', 'is_active'
    ]
    list_filter = ['chart_name', 'chart_type', 'is_active', 'date']
    search_fields = ['chart_name', 'label']
    readonly_fields = ['created_at']
    list_editable = ['is_active']
    ordering = ['chart_name', 'date', 'label']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Información del Gráfico', {
            'fields': ('chart_name', 'chart_type', 'label')
        }),
        ('Datos', {
            'fields': ('value', 'date', 'color')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def formatted_value(self, obj):
        """Muestra el valor formateado según el tipo de gráfico"""
        if obj.chart_name == 'Ventas Mensuales':
            return f"${obj.value:,.0f}"
        elif obj.chart_name == 'Propiedades por Tipo':
            return f"{obj.value}%"
        return f"{obj.value:,.0f}"
    formatted_value.short_description = 'Valor'
    
    def color_preview(self, obj):
        """Muestra una preview del color"""
        if obj.color:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
                obj.color
            )
        return '-'
    color_preview.short_description = 'Color'
    
    actions = ['activate_data', 'deactivate_data']
    
    def activate_data(self, request, queryset):
        """Activa los datos seleccionados"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} datos de gráfico activados.')
    activate_data.short_description = 'Activar datos seleccionados'
    
    def deactivate_data(self, request, queryset):
        """Desactiva los datos seleccionados"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} datos de gráfico desactivados.')
    deactivate_data.short_description = 'Desactivar datos seleccionados'


@admin.register(RecentActivity)
class RecentActivityAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'activity_type', 'user', 'read_status_badge',
        'color_badge', 'time_since_display', 'is_read', 'created_at'
    ]
    list_filter = ['activity_type', 'is_read', 'color', 'created_at']
    search_fields = ['title', 'description', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'time_since_display']
    list_editable = ['is_read']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información de la Actividad', {
            'fields': ('activity_type', 'title', 'description', 'user')
        }),
        ('Presentación', {
            'fields': ('icon', 'color')
        }),
        ('Estado', {
            'fields': ('is_read',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'time_since_display'),
            'classes': ('collapse',)
        })
    )
    
    def read_status_badge(self, obj):
        """Muestra el estado de lectura con badge"""
        if obj.is_read:
            return format_html('<span class="badge badge-success">Leído</span>')
        else:
            return format_html('<span class="badge badge-warning">No leído</span>')
    read_status_badge.short_description = 'Estado'
    
    def color_badge(self, obj):
        """Muestra el color con badge"""
        color_map = {
            'primary': '#007bff',
            'success': '#28a745',
            'info': '#17a2b8',
            'warning': '#ffc107',
            'danger': '#dc3545',
            'secondary': '#6c757d'
        }
        color_hex = color_map.get(obj.color, '#6c757d')
        
        return format_html(
            '<span class="badge" style="background-color: {}; color: white;">{}</span>',
            color_hex, obj.color.title()
        )
    color_badge.short_description = 'Color'
    
    def time_since_display(self, obj):
        """Muestra el tiempo transcurrido"""
        return obj.time_since_created()
    time_since_display.short_description = 'Tiempo Transcurrido'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """Marca las actividades como leídas"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} actividades marcadas como leídas.')
    mark_as_read.short_description = 'Marcar como leídas'
    
    def mark_as_unread(self, request, queryset):
        """Marca las actividades como no leídas"""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} actividades marcadas como no leídas.')
    mark_as_unread.short_description = 'Marcar como no leídas'


# Personalización del admin site
admin.site.site_header = 'URBANY - Dashboard Admin'
admin.site.site_title = 'Dashboard Admin'
admin.site.index_title = 'Administración del Dashboard'

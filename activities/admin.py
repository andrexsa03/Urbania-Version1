from django.contrib import admin
from django.utils.html import format_html
from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'tipo', 'estado_badge', 'prioridad_badge', 
        'asignado_a', 'fecha_programada', 'is_overdue_badge'
    ]
    list_filter = [
        'tipo', 'estado', 'prioridad', 'asignado_a', 
        'creado_por', 'fecha_programada', 'created_at'
    ]
    search_fields = ['titulo', 'descripcion', 'notas', 'ubicacion']
    readonly_fields = ['creado_por', 'fecha_completada', 'created_at', 'updated_at']
    date_hierarchy = 'fecha_programada'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo')
        }),
        ('Estado y Prioridad', {
            'fields': ('estado', 'prioridad')
        }),
        ('Fechas', {
            'fields': ('fecha_programada', 'fecha_vencimiento', 'fecha_completada')
        }),
        ('Asignación', {
            'fields': ('asignado_a', 'creado_por')
        }),
        ('Detalles Adicionales', {
            'fields': ('notas', 'ubicacion', 'duracion_estimada'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def estado_badge(self, obj):
        color = obj.get_status_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    def prioridad_badge(self, obj):
        color = obj.get_priority_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_prioridad_display()
        )
    prioridad_badge.short_description = 'Prioridad'
    
    def is_overdue_badge(self, obj):
        if obj.is_overdue:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">VENCIDA</span>'
            )
        elif obj.is_today:
            return format_html(
                '<span style="background-color: #007bff; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px;">HOY</span>'
            )
        return '-'
    is_overdue_badge.short_description = 'Estado Temporal'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('asignado_a', 'creado_por')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es una nueva actividad
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)

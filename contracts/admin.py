from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Contract, ContractPayment, ContractDocument, ContractNote


@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'contract_type', 'status_badge', 'priority_badge', 'agent', 
        'client_name', 'property_address', 'start_date', 'end_date', 'contract_value', 
        'progress_percentage', 'status', 'priority', 'created_at'
    ]
    list_filter = [
        'contract_type', 'status', 'priority', 'agent', 'start_date', 'end_date', 'created_at'
    ]
    search_fields = [
        'title', 'description', 'client_name', 'client_email', 'property_address', 
        'agent__username', 'agent__email'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'progress_percentage'
    ]
    list_editable = ['status', 'priority']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'contract_type', 'status', 'priority')
        }),
        ('Partes del Contrato', {
            'fields': ('agent', 'client_name', 'client_email', 'client_phone')
        }),
        ('Detalles de la Propiedad', {
            'fields': ('property_address', 'property_type', 'property_size', 'property_value')
        }),
        ('Fechas y Términos', {
            'fields': ('start_date', 'end_date', 'contract_value', 'commission_rate', 'terms_and_conditions')
        }),
        ('Documentos y Notas', {
            'fields': ('contract_file', 'attachments', 'notes')
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Información Calculada', {
            'fields': ('progress_percentage',),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        """Muestra el estado como badge con color"""
        color = obj.get_status_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def priority_badge(self, obj):
        """Muestra la prioridad como badge con color"""
        color = obj.get_priority_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_priority_display()
        )
    priority_badge.short_description = 'Prioridad'
    
    def progress_percentage(self, obj):
        """Muestra el porcentaje de progreso"""
        progress = obj.get_progress_percentage()
        return f"{progress}%"
    progress_percentage.short_description = 'Progreso'
    
    actions = ['mark_as_active', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_active(self, request, queryset):
        """Marca contratos como activos"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} contratos marcados como activos.')
    mark_as_active.short_description = "Marcar como activos"
    
    def mark_as_completed(self, request, queryset):
        """Marca contratos como completados"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} contratos marcados como completados.')
    mark_as_completed.short_description = "Marcar como completados"
    
    def mark_as_cancelled(self, request, queryset):
        """Marca contratos como cancelados"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} contratos marcados como cancelados.')
    mark_as_cancelled.short_description = "Marcar como cancelados"


@admin.register(ContractPayment)
class ContractPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'contract', 'payment_type', 'amount', 'due_date', 'status_badge', 
        'is_overdue', 'status', 'created_at'
    ]
    list_filter = ['payment_type', 'status', 'due_date', 'created_at']
    search_fields = ['contract__title', 'description', 'reference_number']
    readonly_fields = ['created_at', 'updated_at', 'is_overdue']
    list_editable = ['status']
    ordering = ['-due_date']
    date_hierarchy = 'due_date'
    list_per_page = 25
    
    fieldsets = (
        ('Información del Pago', {
            'fields': ('contract', 'payment_type', 'amount', 'due_date', 'status')
        }),
        ('Detalles', {
            'fields': ('description', 'reference_number', 'notes')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'is_overdue'),
            'classes': ('collapse',)
        })
    )
    
    def status_badge(self, obj):
        """Muestra el estado del pago como badge"""
        colors = {
            'pending': '#ffc107',
            'paid': '#28a745',
            'overdue': '#dc3545',
            'cancelled': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def is_overdue(self, obj):
        """Indica si el pago está vencido"""
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = 'Vencido'


@admin.register(ContractDocument)
class ContractDocumentAdmin(admin.ModelAdmin):
    list_display = [
        'contract', 'document_type', 'name', 'file_size_formatted', 
        'uploaded_by', 'uploaded_at'
    ]
    list_filter = ['document_type', 'uploaded_at', 'uploaded_by']
    search_fields = ['contract__title', 'name', 'description']
    readonly_fields = ['uploaded_at', 'file_size_formatted']
    ordering = ['-uploaded_at']
    date_hierarchy = 'uploaded_at'
    list_per_page = 25
    
    fieldsets = (
        ('Información del Documento', {
            'fields': ('contract', 'document_type', 'name', 'file_path')
        }),
        ('Detalles', {
            'fields': ('description', 'file_size', 'uploaded_by')
        }),
        ('Fechas', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        })
    )
    
    def file_size_formatted(self, obj):
        """Formatea el tamaño del archivo"""
        if obj.file_size:
            if obj.file_size < 1024:
                return f"{obj.file_size} B"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.1f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.1f} MB"
        return "N/A"
    file_size_formatted.short_description = 'Tamaño'


@admin.register(ContractNote)
class ContractNoteAdmin(admin.ModelAdmin):
    list_display = [
        'contract', 'note_type', 'title', 'importance_badge', 
        'created_by', 'created_at'
    ]
    list_filter = ['note_type', 'is_important', 'created_at', 'created_by']
    search_fields = ['contract__title', 'title', 'content']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    
    fieldsets = (
        ('Información de la Nota', {
            'fields': ('contract', 'note_type', 'title', 'is_important')
        }),
        ('Contenido', {
            'fields': ('content',)
        }),
        ('Metadatos', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        })
    )
    
    def importance_badge(self, obj):
        """Muestra la importancia como badge"""
        if obj.is_important:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">Importante</span>'
            )
        else:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; '
                'border-radius: 12px; font-size: 11px; font-weight: bold;">Normal</span>'
            )
    importance_badge.short_description = 'Importancia'

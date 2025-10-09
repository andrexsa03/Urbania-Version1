from django.contrib import admin
from .models import MenuSection, UserNavigation, Notification


@admin.register(MenuSection)
class MenuSectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'icon', 'parent', 'order', 'is_active']
    list_filter = ['is_active', 'parent', 'section_type']
    search_fields = ['name', 'url']
    ordering = ['parent', 'order', 'name']
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'url', 'icon', 'section_type')
        }),
        ('Jerarquía', {
            'fields': ('parent', 'order')
        }),
        ('Permisos', {
            'fields': ('requires_permission', 'is_active')
        }),
    )


@admin.register(UserNavigation)
class UserNavigationAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_section', 'last_accessed']
    list_filter = ['current_section', 'last_accessed']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['last_accessed']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at', 'priority']
    search_fields = ['title', 'message', 'user__username']
    readonly_fields = ['created_at']
    list_editable = ['is_read']
    
    fieldsets = (
        ('Contenido', {
            'fields': ('title', 'message', 'notification_type', 'priority')
        }),
        ('Destinatario', {
            'fields': ('user',)
        }),
        ('Estado', {
            'fields': ('is_read', 'is_active', 'created_at', 'read_at')
        }),
        ('Acción', {
            'fields': ('action_url',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

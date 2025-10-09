from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Conversation, Message, MessageRead, MessageReaction, UserStatus


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'conversation_type', 'created_by', 'participants_count', 'last_message_preview', 'created_at', 'is_active']
    list_filter = ['conversation_type', 'is_active', 'created_at']
    search_fields = ['title', 'created_by__first_name', 'created_by__last_name', 'created_by__email']
    readonly_fields = ['created_at', 'updated_at', 'last_message_info']
    filter_horizontal = ['participants']
    
    fieldsets = [
        ('Información Básica', {
            'fields': ['title', 'conversation_type', 'created_by', 'is_active']
        }),
        ('Participantes', {
            'fields': ['participants']
        }),
        ('Metadatos', {
            'fields': ['created_at', 'updated_at', 'last_message_info'],
            'classes': ['collapse']
        })
    ]
    
    def participants_count(self, obj):
        return obj.participants.count()
    participants_count.short_description = 'Participantes'
    
    def last_message_preview(self, obj):
        last_msg = obj.last_message
        if last_msg:
            content = last_msg.content[:50] + '...' if len(last_msg.content) > 50 else last_msg.content
            return format_html(
                '<span title="{}">{}</span>',
                last_msg.content,
                content
            )
        return 'Sin mensajes'
    last_message_preview.short_description = 'Último Mensaje'
    
    def last_message_info(self, obj):
        last_msg = obj.last_message
        if last_msg:
            return format_html(
                '<strong>Remitente:</strong> {}<br>'
                '<strong>Fecha:</strong> {}<br>'
                '<strong>Tipo:</strong> {}<br>'
                '<strong>Leído:</strong> {}',
                last_msg.sender.get_full_name(),
                last_msg.created_at.strftime('%d/%m/%Y %H:%M'),
                last_msg.get_message_type_display(),
                'Sí' if last_msg.is_read else 'No'
            )
        return 'Sin mensajes'
    last_message_info.short_description = 'Información del Último Mensaje'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'conversation_link', 'message_type', 'content_preview', 'is_read', 'created_at']
    list_filter = ['message_type', 'is_read', 'is_deleted', 'created_at']
    search_fields = ['content', 'sender__first_name', 'sender__last_name', 'sender__email']
    readonly_fields = ['created_at', 'updated_at', 'read_at', 'attachment_info']
    raw_id_fields = ['conversation', 'sender', 'reply_to']
    
    fieldsets = [
        ('Información del Mensaje', {
            'fields': ['conversation', 'sender', 'message_type', 'content']
        }),
        ('Archivo Adjunto', {
            'fields': ['attachment', 'attachment_info'],
            'classes': ['collapse']
        }),
        ('Respuesta', {
            'fields': ['reply_to'],
            'classes': ['collapse']
        }),
        ('Estado', {
            'fields': ['is_read', 'is_deleted', 'read_at']
        }),
        ('Metadatos', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        })
    ]
    
    def conversation_link(self, obj):
        url = reverse('admin:messaging_conversation_change', args=[obj.conversation.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.conversation))
    conversation_link.short_description = 'Conversación'
    
    def content_preview(self, obj):
        if obj.message_type == 'text':
            content = obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
            return format_html('<span title="{}">{}</span>', obj.content, content)
        elif obj.message_type == 'file':
            return format_html('<strong>Archivo:</strong> {}', obj.attachment_name or 'Sin nombre')
        elif obj.message_type == 'image':
            return format_html('<strong>Imagen:</strong> {}', obj.attachment_name or 'Sin nombre')
        else:
            return obj.get_message_type_display()
    content_preview.short_description = 'Contenido'
    
    def attachment_info(self, obj):
        if obj.attachment:
            return format_html(
                '<strong>Archivo:</strong> {}<br>'
                '<strong>Tamaño:</strong> {} bytes<br>'
                '<a href="{}" target="_blank">Ver archivo</a>',
                obj.attachment.name,
                obj.attachment.size,
                obj.attachment.url
            )
        return 'Sin archivo adjunto'
    attachment_info.short_description = 'Información del Archivo'


@admin.register(MessageRead)
class MessageReadAdmin(admin.ModelAdmin):
    list_display = ['id', 'message_link', 'user', 'read_at']
    list_filter = ['read_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['read_at']
    raw_id_fields = ['message', 'user']
    
    def message_link(self, obj):
        url = reverse('admin:messaging_message_change', args=[obj.message.id])
        return format_html('<a href="{}">Mensaje #{}</a>', url, obj.message.id)
    message_link.short_description = 'Mensaje'


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'message_link', 'user', 'reaction_display', 'created_at']
    list_filter = ['reaction_type', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['created_at']
    raw_id_fields = ['message', 'user']
    
    def message_link(self, obj):
        url = reverse('admin:messaging_message_change', args=[obj.message.id])
        return format_html('<a href="{}">Mensaje #{}</a>', url, obj.message.id)
    message_link.short_description = 'Mensaje'
    
    def reaction_display(self, obj):
        return f"{obj.get_reaction_type_display()} ({obj.reaction_type})"
    reaction_display.short_description = 'Reacción'


@admin.register(UserStatus)
class UserStatusAdmin(admin.ModelAdmin):
    list_display = ['user', 'status_display', 'last_seen', 'custom_message']
    list_filter = ['status', 'last_seen']
    search_fields = ['user__first_name', 'user__last_name', 'user__email']
    readonly_fields = ['last_seen']
    
    def status_display(self, obj):
        colors = {
            'online': 'green',
            'away': 'orange',
            'busy': 'red',
            'offline': 'gray'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {};">● {}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Estado'
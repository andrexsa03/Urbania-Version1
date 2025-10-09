from rest_framework import serializers
from .models import MenuSection, UserNavigation, Notification


class MenuSectionSerializer(serializers.ModelSerializer):
    """
    Serializer para las secciones del menú
    """
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = MenuSection
        fields = [
            'id', 'name', 'slug', 'icon', 'url', 'section_type',
            'order', 'is_active', 'requires_permission', 'parent',
            'children', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_children(self, obj):
        """Obtener subsecciones hijas"""
        children = MenuSection.objects.filter(parent=obj, is_active=True).order_by('order')
        return MenuSectionSerializer(children, many=True, context=self.context).data


class UserNavigationSerializer(serializers.ModelSerializer):
    """
    Serializer para la navegación del usuario
    """
    current_section = MenuSectionSerializer(read_only=True)
    current_section_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = UserNavigation
        fields = [
            'id', 'user', 'current_section', 'current_section_id',
            'last_accessed'
        ]
        read_only_fields = ['id', 'user', 'last_accessed']
    
    def create(self, validated_data):
        """Crear o actualizar navegación del usuario"""
        user = self.context['request'].user
        current_section_id = validated_data.pop('current_section_id')
        
        # Obtener o crear la navegación del usuario
        user_nav, created = UserNavigation.objects.get_or_create(
            user=user,
            defaults={'current_section_id': current_section_id}
        )
        
        if not created:
            user_nav.current_section_id = current_section_id
            user_nav.save()
        
        return user_nav


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer para notificaciones
    """
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'title', 'message', 'notification_type',
            'priority', 'is_read', 'is_active', 'action_url',
            'created_at', 'read_at', 'time_since_created'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'read_at', 'time_since_created']
    
    def get_time_since_created(self, obj):
        """Calcular tiempo transcurrido desde la creación"""
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        return timesince(obj.created_at, timezone.now())


class NotificationMarkReadSerializer(serializers.Serializer):
    """
    Serializer para marcar notificaciones como leídas
    """
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="Lista de IDs de notificaciones a marcar como leídas"
    )


class NavigationMenuSerializer(serializers.Serializer):
    """
    Serializer para el menú completo de navegación
    """
    sections = MenuSectionSerializer(many=True, read_only=True)
    current_section = MenuSectionSerializer(read_only=True)
    notifications_count = serializers.IntegerField(read_only=True)
    unread_notifications = serializers.IntegerField(read_only=True)
    user_permissions = serializers.ListField(
        child=serializers.CharField(),
        read_only=True
    )
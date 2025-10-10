from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Alert, AlertTemplate, AlertRule, AlertLog

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para información de usuario"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class AlertLogSerializer(serializers.ModelSerializer):
    """Serializer para logs de alertas"""
    
    class Meta:
        model = AlertLog
        fields = [
            'id', 'status', 'delivery_method', 'recipient',
            'sent_at', 'delivered_at', 'read_at', 'error_message',
            'created_at'
        ]


class AlertSerializer(serializers.ModelSerializer):
    """Serializer principal para alertas"""
    
    user = UserBasicSerializer(read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    logs = AlertLogSerializer(many=True, read_only=True)
    
    # Campos calculados
    is_expired = serializers.SerializerMethodField()
    time_until_scheduled = serializers.SerializerMethodField()
    priority_color = serializers.SerializerMethodField()
    type_icon = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    type_display = serializers.CharField(source='get_alert_type_display', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    days_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'title', 'message', 'alert_type', 'priority', 'status',
            'user', 'created_by', 'scheduled_at', 'expires_at', 'frequency',
            'icon', 'color', 'action_url', 'action_text', 'is_recurring',
            'is_system_alert', 'send_email', 'send_push', 'created_at',
            'updated_at', 'read_at', 'dismissed_at', 'logs',
            # Campos calculados
            'is_expired', 'time_until_scheduled', 'priority_color', 'type_icon',
            'status_display', 'priority_display', 'type_display', 'frequency_display',
            'days_since_created'
        ]
    
    def get_is_expired(self, obj):
        return obj.is_expired()
    
    def get_time_until_scheduled(self, obj):
        delta = obj.time_until_scheduled()
        if delta.total_seconds() > 0:
            hours = int(delta.total_seconds() // 3600)
            minutes = int((delta.total_seconds() % 3600) // 60)
            return f"{hours}h {minutes}m"
        return "Vencida"
    
    def get_priority_color(self, obj):
        return obj.get_priority_color()
    
    def get_type_icon(self, obj):
        return obj.get_type_icon()
    
    def get_days_since_created(self, obj):
        delta = timezone.now() - obj.created_at
        return delta.days


class AlertCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear alertas"""
    
    class Meta:
        model = Alert
        fields = [
            'title', 'message', 'alert_type', 'priority', 'user',
            'scheduled_at', 'expires_at', 'frequency', 'icon', 'color',
            'action_url', 'action_text', 'is_recurring', 'send_email',
            'send_push'
        ]
    
    def validate_scheduled_at(self, value):
        """Valida que la fecha programada no sea en el pasado"""
        if value < timezone.now():
            raise serializers.ValidationError(
                "La fecha programada no puede ser en el pasado"
            )
        return value
    
    def validate_expires_at(self, value):
        """Valida que la fecha de expiración sea posterior a la programada"""
        if value and self.initial_data.get('scheduled_at'):
            scheduled_at = self.initial_data['scheduled_at']
            if isinstance(scheduled_at, str):
                from django.utils.dateparse import parse_datetime
                scheduled_at = parse_datetime(scheduled_at)
            
            if value <= scheduled_at:
                raise serializers.ValidationError(
                    "La fecha de expiración debe ser posterior a la fecha programada"
                )
        return value
    
    def create(self, validated_data):
        """Crea una nueva alerta"""
        # Asignar el usuario actual como creador
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        
        # Si no se especifica usuario, usar el creador
        if not validated_data.get('user'):
            validated_data['user'] = validated_data['created_by']
        
        return super().create(validated_data)


class AlertUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar alertas"""
    
    class Meta:
        model = Alert
        fields = [
            'title', 'message', 'alert_type', 'priority', 'status',
            'scheduled_at', 'expires_at', 'frequency', 'icon', 'color',
            'action_url', 'action_text', 'is_recurring', 'send_email',
            'send_push'
        ]
    
    def validate_status(self, value):
        """Valida transiciones de estado válidas"""
        if self.instance:
            current_status = self.instance.status
            
            # Reglas de transición
            valid_transitions = {
                'active': ['read', 'dismissed', 'expired'],
                'read': ['dismissed'],
                'dismissed': [],  # No se puede cambiar desde dismissed
                'expired': ['dismissed']
            }
            
            if value != current_status and value not in valid_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"No se puede cambiar el estado de '{current_status}' a '{value}'"
                )
        
        return value


class AlertListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de alertas"""
    
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    priority_color = serializers.SerializerMethodField()
    type_icon = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Alert
        fields = [
            'id', 'title', 'alert_type', 'priority', 'status',
            'user_name', 'scheduled_at', 'created_at', 'priority_color',
            'type_icon', 'status_display', 'is_expired'
        ]
    
    def get_priority_color(self, obj):
        return obj.get_priority_color()
    
    def get_type_icon(self, obj):
        return obj.get_type_icon()
    
    def get_is_expired(self, obj):
        return obj.is_expired()


class AlertTemplateSerializer(serializers.ModelSerializer):
    """Serializer para plantillas de alertas"""
    
    created_by = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = AlertTemplate
        fields = [
            'id', 'name', 'description', 'title_template', 'message_template',
            'alert_type', 'priority', 'frequency', 'advance_time', 'icon',
            'color', 'is_active', 'created_by', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """Crea una nueva plantilla"""
        request = self.context.get('request')
        if request and request.user:
            validated_data['created_by'] = request.user
        return super().create(validated_data)


class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer para reglas de alertas"""
    
    template = AlertTemplateSerializer(read_only=True)
    template_id = serializers.IntegerField(write_only=True)
    target_users = UserBasicSerializer(many=True, read_only=True)
    target_user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = AlertRule
        fields = [
            'id', 'name', 'description', 'trigger_type', 'trigger_condition',
            'template', 'template_id', 'is_active', 'target_users',
            'target_user_ids', 'created_at', 'updated_at', 'last_triggered'
        ]
    
    def create(self, validated_data):
        """Crea una nueva regla"""
        target_user_ids = validated_data.pop('target_user_ids', [])
        rule = super().create(validated_data)
        
        if target_user_ids:
            users = User.objects.filter(id__in=target_user_ids)
            rule.target_users.set(users)
        
        return rule
    
    def update(self, instance, validated_data):
        """Actualiza una regla existente"""
        target_user_ids = validated_data.pop('target_user_ids', None)
        rule = super().update(instance, validated_data)
        
        if target_user_ids is not None:
            users = User.objects.filter(id__in=target_user_ids)
            rule.target_users.set(users)
        
        return rule


class AlertStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de alertas"""
    
    total_alerts = serializers.IntegerField()
    active_alerts = serializers.IntegerField()
    read_alerts = serializers.IntegerField()
    dismissed_alerts = serializers.IntegerField()
    expired_alerts = serializers.IntegerField()
    
    # Por prioridad
    urgent_alerts = serializers.IntegerField()
    high_priority_alerts = serializers.IntegerField()
    medium_priority_alerts = serializers.IntegerField()
    low_priority_alerts = serializers.IntegerField()
    
    # Por tipo
    reminder_alerts = serializers.IntegerField()
    notification_alerts = serializers.IntegerField()
    warning_alerts = serializers.IntegerField()
    info_alerts = serializers.IntegerField()
    success_alerts = serializers.IntegerField()
    error_alerts = serializers.IntegerField()
    
    # Métricas de tiempo
    alerts_today = serializers.IntegerField()
    alerts_this_week = serializers.IntegerField()
    alerts_this_month = serializers.IntegerField()
    
    # Métricas de rendimiento
    avg_response_time = serializers.FloatField()
    read_rate = serializers.FloatField()


class AlertBulkActionSerializer(serializers.Serializer):
    """Serializer para acciones en lote"""
    
    ACTION_CHOICES = [
        ('mark_read', 'Marcar como leídas'),
        ('dismiss', 'Descartar'),
        ('delete', 'Eliminar'),
        ('change_priority', 'Cambiar prioridad'),
    ]
    
    alert_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    priority = serializers.ChoiceField(
        choices=Alert.PRIORITY_LEVELS,
        required=False
    )
    
    def validate(self, data):
        """Valida que los datos sean consistentes"""
        if data['action'] == 'change_priority' and not data.get('priority'):
            raise serializers.ValidationError(
                "La prioridad es requerida para la acción 'change_priority'"
            )
        return data


class AlertSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de alertas"""
    
    query = serializers.CharField(required=False, allow_blank=True)
    alert_type = serializers.ChoiceField(
        choices=Alert.ALERT_TYPES,
        required=False
    )
    priority = serializers.ChoiceField(
        choices=Alert.PRIORITY_LEVELS,
        required=False
    )
    status = serializers.ChoiceField(
        choices=Alert.STATUS_CHOICES,
        required=False
    )
    user_id = serializers.IntegerField(required=False)
    date_from = serializers.DateTimeField(required=False)
    date_to = serializers.DateTimeField(required=False)
    is_recurring = serializers.BooleanField(required=False)
    is_system_alert = serializers.BooleanField(required=False)


class AlertGenerateSerializer(serializers.Serializer):
    """Serializer para generar alertas mock"""
    
    count = serializers.IntegerField(min_value=1, max_value=100, default=10)
    user_id = serializers.IntegerField(required=False)
    
    def validate_user_id(self, value):
        """Valida que el usuario exista"""
        if value:
            try:
                User.objects.get(id=value)
            except User.DoesNotExist:
                raise serializers.ValidationError("El usuario no existe")
        return value
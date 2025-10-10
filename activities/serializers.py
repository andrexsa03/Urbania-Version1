from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Activity

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para mostrar información del usuario"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'email']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class ActivitySerializer(serializers.ModelSerializer):
    """Serializer completo para actividades"""
    asignado_a_info = UserBasicSerializer(source='asignado_a', read_only=True)
    creado_por_info = UserBasicSerializer(source='creado_por', read_only=True)
    
    # Campos calculados
    is_overdue = serializers.ReadOnlyField()
    is_today = serializers.ReadOnlyField()
    priority_color = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    
    # Campos de display para choices
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    
    class Meta:
        model = Activity
        fields = [
            'id', 'titulo', 'descripcion', 'tipo', 'tipo_display',
            'estado', 'estado_display', 'prioridad', 'prioridad_display',
            'fecha_programada', 'fecha_vencimiento', 'fecha_completada',
            'asignado_a', 'asignado_a_info', 'creado_por', 'creado_por_info',
            'notas', 'ubicacion', 'duracion_estimada',
            'is_overdue', 'is_today', 'priority_color', 'status_color',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['creado_por', 'fecha_completada', 'created_at', 'updated_at']
    
    def get_priority_color(self, obj):
        return obj.get_priority_color()
    
    def get_status_color(self, obj):
        return obj.get_status_color()
    
    def create(self, validated_data):
        # Asignar el usuario actual como creador
        validated_data['creado_por'] = self.context['request'].user
        return super().create(validated_data)


class ActivityCreateSerializer(serializers.ModelSerializer):
    """Serializer simplificado para crear actividades"""
    
    class Meta:
        model = Activity
        fields = [
            'titulo', 'descripcion', 'tipo', 'estado', 'prioridad',
            'fecha_programada', 'fecha_vencimiento', 'asignado_a',
            'notas', 'ubicacion', 'duracion_estimada'
        ]
    
    def create(self, validated_data):
        validated_data['creado_por'] = self.context['request'].user
        return super().create(validated_data)


class ActivityUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar actividades"""
    
    class Meta:
        model = Activity
        fields = [
            'titulo', 'descripcion', 'tipo', 'estado', 'prioridad',
            'fecha_programada', 'fecha_vencimiento', 'asignado_a',
            'notas', 'ubicacion', 'duracion_estimada'
        ]


class ActivityListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de actividades"""
    asignado_a_nombre = serializers.CharField(source='asignado_a.get_full_name', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    
    is_overdue = serializers.ReadOnlyField()
    is_today = serializers.ReadOnlyField()
    priority_color = serializers.SerializerMethodField()
    status_color = serializers.SerializerMethodField()
    
    class Meta:
        model = Activity
        fields = [
            'id', 'titulo', 'tipo', 'tipo_display', 'estado', 'estado_display',
            'prioridad', 'prioridad_display', 'fecha_programada', 'fecha_vencimiento',
            'asignado_a', 'asignado_a_nombre', 'ubicacion',
            'is_overdue', 'is_today', 'priority_color', 'status_color'
        ]
    
    def get_priority_color(self, obj):
        return obj.get_priority_color()
    
    def get_status_color(self, obj):
        return obj.get_status_color()


class ActivityStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de actividades"""
    total_actividades = serializers.IntegerField()
    pendientes = serializers.IntegerField()
    en_progreso = serializers.IntegerField()
    completadas = serializers.IntegerField()
    vencidas = serializers.IntegerField()
    hoy = serializers.IntegerField()
    esta_semana = serializers.IntegerField()
    por_tipo = serializers.DictField()
    por_prioridad = serializers.DictField()


class ActivityMarkCompleteSerializer(serializers.Serializer):
    """Serializer para marcar actividades como completadas"""
    notas_finales = serializers.CharField(required=False, allow_blank=True)
    
    def update(self, instance, validated_data):
        instance.marcar_completada()
        if validated_data.get('notas_finales'):
            if instance.notas:
                instance.notas += f"\n\nNotas finales: {validated_data['notas_finales']}"
            else:
                instance.notas = f"Notas finales: {validated_data['notas_finales']}"
            instance.save()
        return instance
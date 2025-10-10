from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django_filters.rest_framework import DjangoFilterBackend
from datetime import timedelta
import json

from .models import Alert, AlertTemplate, AlertRule, AlertLog
from .serializers import (
    AlertSerializer, AlertCreateSerializer, AlertUpdateSerializer,
    AlertListSerializer, AlertTemplateSerializer, AlertRuleSerializer,
    AlertStatsSerializer, AlertBulkActionSerializer, AlertSearchSerializer,
    AlertGenerateSerializer
)

User = get_user_model()


class AlertListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear alertas"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['alert_type', 'priority', 'status', 'is_recurring', 'is_system_alert']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'scheduled_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtra alertas por usuario"""
        return Alert.objects.filter(user=self.request.user).select_related(
            'user', 'created_by'
        ).prefetch_related('logs')
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.request.method == 'POST':
            return AlertCreateSerializer
        return AlertListSerializer
    
    def perform_create(self, serializer):
        """Personaliza la creación de alertas"""
        serializer.save(created_by=self.request.user)


class AlertDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para detalle, actualización y eliminación de alertas"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra alertas por usuario"""
        return Alert.objects.filter(user=self.request.user).select_related(
            'user', 'created_by'
        ).prefetch_related('logs')
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.request.method in ['PUT', 'PATCH']:
            return AlertUpdateSerializer
        return AlertSerializer


class AlertTemplateListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear plantillas de alertas"""
    
    serializer_class = AlertTemplateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_queryset(self):
        """Filtra plantillas por usuario o públicas"""
        return AlertTemplate.objects.filter(
            Q(created_by=self.request.user) | Q(is_active=True)
        ).select_related('created_by')


class AlertTemplateDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para detalle de plantillas de alertas"""
    
    serializer_class = AlertTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra plantillas por usuario"""
        return AlertTemplate.objects.filter(
            created_by=self.request.user
        ).select_related('created_by')


class AlertRuleListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear reglas de alertas"""
    
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at', 'last_triggered']
    ordering = ['name']
    
    def get_queryset(self):
        """Filtra reglas que incluyan al usuario"""
        return AlertRule.objects.filter(
            Q(target_users=self.request.user) | Q(target_users__isnull=True)
        ).select_related('template').prefetch_related('target_users')


class AlertRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para detalle de reglas de alertas"""
    
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtra reglas que incluyan al usuario"""
        return AlertRule.objects.filter(
            Q(target_users=self.request.user) | Q(target_users__isnull=True)
        ).select_related('template').prefetch_related('target_users')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def alert_stats(request):
    """Estadísticas de alertas del usuario"""
    
    user_alerts = Alert.objects.filter(user=request.user)
    
    # Estadísticas básicas
    total_alerts = user_alerts.count()
    active_alerts = user_alerts.filter(status='active').count()
    read_alerts = user_alerts.filter(status='read').count()
    dismissed_alerts = user_alerts.filter(status='dismissed').count()
    expired_alerts = user_alerts.filter(status='expired').count()
    
    # Por prioridad
    urgent_alerts = user_alerts.filter(priority='urgent').count()
    high_priority_alerts = user_alerts.filter(priority='high').count()
    medium_priority_alerts = user_alerts.filter(priority='medium').count()
    low_priority_alerts = user_alerts.filter(priority='low').count()
    
    # Por tipo
    reminder_alerts = user_alerts.filter(alert_type='reminder').count()
    notification_alerts = user_alerts.filter(alert_type='notification').count()
    warning_alerts = user_alerts.filter(alert_type='warning').count()
    info_alerts = user_alerts.filter(alert_type='info').count()
    success_alerts = user_alerts.filter(alert_type='success').count()
    error_alerts = user_alerts.filter(alert_type='error').count()
    
    # Métricas de tiempo
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())
    month_start = today_start.replace(day=1)
    
    alerts_today = user_alerts.filter(created_at__gte=today_start).count()
    alerts_this_week = user_alerts.filter(created_at__gte=week_start).count()
    alerts_this_month = user_alerts.filter(created_at__gte=month_start).count()
    
    # Métricas de rendimiento
    read_alerts_with_time = user_alerts.filter(
        status='read',
        read_at__isnull=False
    )
    
    avg_response_time = 0
    if read_alerts_with_time.exists():
        response_times = []
        for alert in read_alerts_with_time:
            if alert.read_at and alert.created_at:
                delta = alert.read_at - alert.created_at
                response_times.append(delta.total_seconds() / 3600)  # en horas
        
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
    
    read_rate = (read_alerts / total_alerts * 100) if total_alerts > 0 else 0
    
    stats_data = {
        'total_alerts': total_alerts,
        'active_alerts': active_alerts,
        'read_alerts': read_alerts,
        'dismissed_alerts': dismissed_alerts,
        'expired_alerts': expired_alerts,
        'urgent_alerts': urgent_alerts,
        'high_priority_alerts': high_priority_alerts,
        'medium_priority_alerts': medium_priority_alerts,
        'low_priority_alerts': low_priority_alerts,
        'reminder_alerts': reminder_alerts,
        'notification_alerts': notification_alerts,
        'warning_alerts': warning_alerts,
        'info_alerts': info_alerts,
        'success_alerts': success_alerts,
        'error_alerts': error_alerts,
        'alerts_today': alerts_today,
        'alerts_this_week': alerts_this_week,
        'alerts_this_month': alerts_this_month,
        'avg_response_time': round(avg_response_time, 2),
        'read_rate': round(read_rate, 2)
    }
    
    serializer = AlertStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_alert_read(request, pk):
    """Marca una alerta como leída"""
    
    try:
        alert = Alert.objects.get(pk=pk, user=request.user)
        alert.mark_as_read()
        
        serializer = AlertSerializer(alert)
        return Response(serializer.data)
    
    except Alert.DoesNotExist:
        return Response(
            {'error': 'Alerta no encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def dismiss_alert(request, pk):
    """Descarta una alerta"""
    
    try:
        alert = Alert.objects.get(pk=pk, user=request.user)
        alert.dismiss()
        
        serializer = AlertSerializer(alert)
        return Response(serializer.data)
    
    except Alert.DoesNotExist:
        return Response(
            {'error': 'Alerta no encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_alert_actions(request):
    """Acciones en lote para alertas"""
    
    serializer = AlertBulkActionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    alert_ids = serializer.validated_data['alert_ids']
    action = serializer.validated_data['action']
    
    # Filtrar alertas del usuario
    alerts = Alert.objects.filter(
        id__in=alert_ids,
        user=request.user
    )
    
    if not alerts.exists():
        return Response(
            {'error': 'No se encontraron alertas válidas'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Ejecutar acción
    updated_count = 0
    
    if action == 'mark_read':
        for alert in alerts:
            if alert.status == 'active':
                alert.mark_as_read()
                updated_count += 1
    
    elif action == 'dismiss':
        for alert in alerts:
            if alert.status in ['active', 'read']:
                alert.dismiss()
                updated_count += 1
    
    elif action == 'delete':
        updated_count = alerts.count()
        alerts.delete()
    
    elif action == 'change_priority':
        priority = serializer.validated_data.get('priority')
        if priority:
            alerts.update(priority=priority)
            updated_count = alerts.count()
    
    return Response({
        'message': f'Acción ejecutada en {updated_count} alertas',
        'updated_count': updated_count
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def search_alerts(request):
    """Búsqueda avanzada de alertas"""
    
    serializer = AlertSearchSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    queryset = Alert.objects.filter(user=request.user)
    
    # Aplicar filtros
    query = serializer.validated_data.get('query')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) | Q(message__icontains=query)
        )
    
    alert_type = serializer.validated_data.get('alert_type')
    if alert_type:
        queryset = queryset.filter(alert_type=alert_type)
    
    priority = serializer.validated_data.get('priority')
    if priority:
        queryset = queryset.filter(priority=priority)
    
    status_filter = serializer.validated_data.get('status')
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    user_id = serializer.validated_data.get('user_id')
    if user_id:
        queryset = queryset.filter(user_id=user_id)
    
    date_from = serializer.validated_data.get('date_from')
    if date_from:
        queryset = queryset.filter(created_at__gte=date_from)
    
    date_to = serializer.validated_data.get('date_to')
    if date_to:
        queryset = queryset.filter(created_at__lte=date_to)
    
    is_recurring = serializer.validated_data.get('is_recurring')
    if is_recurring is not None:
        queryset = queryset.filter(is_recurring=is_recurring)
    
    is_system_alert = serializer.validated_data.get('is_system_alert')
    if is_system_alert is not None:
        queryset = queryset.filter(is_system_alert=is_system_alert)
    
    # Serializar resultados
    alerts = queryset.select_related('user', 'created_by').order_by('-created_at')
    result_serializer = AlertListSerializer(alerts, many=True)
    
    return Response({
        'count': alerts.count(),
        'results': result_serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_active_alerts(request):
    """Alertas activas del usuario actual"""
    
    alerts = Alert.objects.filter(
        user=request.user,
        status='active'
    ).select_related('user', 'created_by').order_by('scheduled_at')
    
    serializer = AlertListSerializer(alerts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def upcoming_alerts(request):
    """Alertas próximas (siguientes 24 horas)"""
    
    now = timezone.now()
    tomorrow = now + timedelta(days=1)
    
    alerts = Alert.objects.filter(
        user=request.user,
        status='active',
        scheduled_at__gte=now,
        scheduled_at__lte=tomorrow
    ).select_related('user', 'created_by').order_by('scheduled_at')
    
    serializer = AlertListSerializer(alerts, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_mock_alerts(request):
    """Genera alertas mock para pruebas"""
    
    serializer = AlertGenerateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    count = serializer.validated_data['count']
    user_id = serializer.validated_data.get('user_id')
    
    # Determinar usuario objetivo
    if user_id:
        try:
            target_user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
    else:
        target_user = request.user
    
    # Generar alertas mock
    alerts = Alert.generate_mock_alerts(target_user, count)
    
    # Serializar respuesta
    result_serializer = AlertListSerializer(alerts, many=True)
    
    return Response({
        'message': f'Se generaron {len(alerts)} alertas mock',
        'count': len(alerts),
        'alerts': result_serializer.data
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_all_alerts(request):
    """Elimina todas las alertas del usuario"""
    
    count = Alert.objects.filter(user=request.user).count()
    Alert.objects.filter(user=request.user).delete()
    
    return Response({
        'message': f'Se eliminaron {count} alertas',
        'deleted_count': count
    })

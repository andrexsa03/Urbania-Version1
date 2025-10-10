from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Activity
from .serializers import (
    ActivitySerializer, ActivityCreateSerializer, ActivityUpdateSerializer,
    ActivityListSerializer, ActivityStatsSerializer, ActivityMarkCompleteSerializer
)


class ActivityListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear actividades.
    GET: Lista actividades con filtros opcionales
    POST: Crea una nueva actividad
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'estado', 'prioridad', 'asignado_a']
    search_fields = ['titulo', 'descripcion', 'notas', 'ubicacion']
    ordering_fields = ['fecha_programada', 'prioridad', 'created_at']
    ordering = ['-fecha_programada']
    
    def get_queryset(self):
        queryset = Activity.objects.select_related('asignado_a', 'creado_por')
        
        # Filtros adicionales por parámetros de query
        estado = self.request.query_params.get('estado')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        solo_pendientes = self.request.query_params.get('solo_pendientes')
        solo_vencidas = self.request.query_params.get('solo_vencidas')
        solo_hoy = self.request.query_params.get('solo_hoy')
        mis_actividades = self.request.query_params.get('mis_actividades')
        
        # Filtrar por estado
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por rango de fechas
        if fecha_desde:
            try:
                fecha_desde = datetime.fromisoformat(fecha_desde.replace('Z', '+00:00'))
                queryset = queryset.filter(fecha_programada__gte=fecha_desde)
            except ValueError:
                pass
        
        if fecha_hasta:
            try:
                fecha_hasta = datetime.fromisoformat(fecha_hasta.replace('Z', '+00:00'))
                queryset = queryset.filter(fecha_programada__lte=fecha_hasta)
            except ValueError:
                pass
        
        # Solo actividades pendientes
        if solo_pendientes == 'true':
            queryset = queryset.filter(estado__in=['pendiente', 'en_progreso'])
        
        # Solo actividades vencidas
        if solo_vencidas == 'true':
            now = timezone.now()
            queryset = queryset.filter(
                fecha_vencimiento__lt=now,
                estado__in=['pendiente', 'en_progreso']
            )
        
        # Solo actividades de hoy
        if solo_hoy == 'true':
            today = timezone.now().date()
            queryset = queryset.filter(fecha_programada__date=today)
        
        # Solo mis actividades
        if mis_actividades == 'true':
            queryset = queryset.filter(asignado_a=self.request.user)
        
        return queryset
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ActivityCreateSerializer
        return ActivityListSerializer


class ActivityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar una actividad específica.
    GET: Obtiene detalles de la actividad
    PUT/PATCH: Actualiza la actividad
    DELETE: Elimina la actividad
    """
    queryset = Activity.objects.select_related('asignado_a', 'creado_por')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ActivityUpdateSerializer
        return ActivitySerializer


class ActivityMarkCompleteView(generics.UpdateAPIView):
    """
    Vista para marcar una actividad como completada.
    PATCH: Marca la actividad como completada
    """
    queryset = Activity.objects.all()
    serializer_class = ActivityMarkCompleteSerializer
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, *args, **kwargs):
        activity = self.get_object()
        serializer = self.get_serializer(activity, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            # Retornar la actividad actualizada
            activity_serializer = ActivitySerializer(activity)
            return Response({
                'message': 'Actividad marcada como completada',
                'activity': activity_serializer.data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def activity_stats(request):
    """
    Endpoint para obtener estadísticas de actividades.
    Retorna conteos por estado, tipo, prioridad, etc.
    """
    user = request.user
    
    # Filtrar por usuario si se especifica
    queryset = Activity.objects.all()
    if request.query_params.get('mis_actividades') == 'true':
        queryset = queryset.filter(asignado_a=user)
    
    # Estadísticas básicas
    total_actividades = queryset.count()
    pendientes = queryset.filter(estado='pendiente').count()
    en_progreso = queryset.filter(estado='en_progreso').count()
    completadas = queryset.filter(estado='completada').count()
    
    # Actividades vencidas
    now = timezone.now()
    vencidas = queryset.filter(
        fecha_vencimiento__lt=now,
        estado__in=['pendiente', 'en_progreso']
    ).count()
    
    # Actividades de hoy
    today = timezone.now().date()
    hoy = queryset.filter(fecha_programada__date=today).count()
    
    # Actividades de esta semana
    start_week = today - timedelta(days=today.weekday())
    end_week = start_week + timedelta(days=6)
    esta_semana = queryset.filter(
        fecha_programada__date__range=[start_week, end_week]
    ).count()
    
    # Estadísticas por tipo
    por_tipo = {}
    for tipo_code, tipo_name in Activity.ACTIVITY_TYPES:
        count = queryset.filter(tipo=tipo_code).count()
        por_tipo[tipo_name] = count
    
    # Estadísticas por prioridad
    por_prioridad = {}
    for prioridad_code, prioridad_name in Activity.PRIORITY_LEVELS:
        count = queryset.filter(prioridad=prioridad_code).count()
        por_prioridad[prioridad_name] = count
    
    stats_data = {
        'total_actividades': total_actividades,
        'pendientes': pendientes,
        'en_progreso': en_progreso,
        'completadas': completadas,
        'vencidas': vencidas,
        'hoy': hoy,
        'esta_semana': esta_semana,
        'por_tipo': por_tipo,
        'por_prioridad': por_prioridad,
    }
    
    serializer = ActivityStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_activities(request):
    """
    Endpoint específico para listar actividades pendientes.
    Retorna solo actividades con estado 'pendiente' o 'en_progreso'.
    """
    user = request.user
    
    # Obtener actividades pendientes
    queryset = Activity.objects.filter(
        estado__in=['pendiente', 'en_progreso']
    ).select_related('asignado_a', 'creado_por')
    
    # Filtrar por usuario si se especifica
    if request.query_params.get('mis_actividades') == 'true':
        queryset = queryset.filter(asignado_a=user)
    
    # Ordenar por prioridad y fecha
    queryset = queryset.order_by('-prioridad', 'fecha_programada')
    
    serializer = ActivityListSerializer(queryset, many=True)
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def overdue_activities(request):
    """
    Endpoint para listar actividades vencidas.
    Retorna actividades que han pasado su fecha de vencimiento.
    """
    user = request.user
    now = timezone.now()
    
    # Obtener actividades vencidas
    queryset = Activity.objects.filter(
        fecha_vencimiento__lt=now,
        estado__in=['pendiente', 'en_progreso']
    ).select_related('asignado_a', 'creado_por')
    
    # Filtrar por usuario si se especifica
    if request.query_params.get('mis_actividades') == 'true':
        queryset = queryset.filter(asignado_a=user)
    
    # Ordenar por fecha de vencimiento
    queryset = queryset.order_by('fecha_vencimiento')
    
    serializer = ActivityListSerializer(queryset, many=True)
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def today_activities(request):
    """
    Endpoint para listar actividades programadas para hoy.
    """
    user = request.user
    today = timezone.now().date()
    
    # Obtener actividades de hoy
    queryset = Activity.objects.filter(
        fecha_programada__date=today
    ).select_related('asignado_a', 'creado_por')
    
    # Filtrar por usuario si se especifica
    if request.query_params.get('mis_actividades') == 'true':
        queryset = queryset.filter(asignado_a=user)
    
    # Ordenar por hora programada
    queryset = queryset.order_by('fecha_programada')
    
    serializer = ActivityListSerializer(queryset, many=True)
    return Response({
        'count': queryset.count(),
        'results': serializer.data
    })

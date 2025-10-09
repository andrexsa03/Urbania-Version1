from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import MenuSection, UserNavigation, Notification
from .serializers import (
    MenuSectionSerializer, UserNavigationSerializer, NotificationSerializer,
    NotificationMarkReadSerializer, NavigationMenuSerializer
)


class NavigationMenuView(generics.GenericAPIView):
    """
    Vista para obtener el menú completo de navegación del usuario
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NavigationMenuSerializer
    
    def get(self, request):
        """
        Obtener menú de navegación con secciones disponibles para el usuario
        """
        user = request.user
        
        # Obtener secciones principales (sin padre) y activas
        main_sections = MenuSection.objects.filter(
            parent__isnull=True,
            is_active=True
        ).order_by('order')
        
        # Filtrar secciones según permisos del usuario
        available_sections = []
        user_permissions = list(user.get_all_permissions()) if hasattr(user, 'get_all_permissions') else []
        
        for section in main_sections:
            if not section.requires_permission or section.requires_permission in user_permissions:
                available_sections.append(section)
        
        # Obtener sección actual del usuario
        current_section = None
        try:
            user_nav = UserNavigation.objects.get(user=user)
            current_section = user_nav.current_section
        except UserNavigation.DoesNotExist:
            # Si no existe, asignar la primera sección disponible
            if available_sections:
                current_section = available_sections[0]
                UserNavigation.objects.create(user=user, current_section=current_section)
        
        # Contar notificaciones
        notifications_count = Notification.objects.filter(user=user, is_active=True).count()
        unread_notifications = Notification.objects.filter(
            user=user, is_active=True, is_read=False
        ).count()
        
        # Preparar datos de respuesta
        data = {
            'sections': MenuSectionSerializer(available_sections, many=True, context={'request': request}).data,
            'current_section': MenuSectionSerializer(current_section, context={'request': request}).data if current_section else None,
            'notifications_count': notifications_count,
            'unread_notifications': unread_notifications,
            'user_permissions': user_permissions
        }
        
        return Response(data, status=status.HTTP_200_OK)


class UpdateCurrentSectionView(generics.CreateAPIView):
    """
    Vista para actualizar la sección actual del usuario
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UserNavigationSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Actualizar sección actual del usuario
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user_nav = serializer.save()
        
        return Response({
            'message': 'Sección actualizada correctamente',
            'current_section': MenuSectionSerializer(user_nav.current_section).data
        }, status=status.HTTP_200_OK)


class NotificationListView(generics.ListAPIView):
    """
    Vista para listar notificaciones del usuario
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        """
        Obtener notificaciones del usuario autenticado
        """
        user = self.request.user
        queryset = Notification.objects.filter(user=user, is_active=True)
        
        # Filtros opcionales
        is_read = self.request.query_params.get('is_read')
        notification_type = self.request.query_params.get('type')
        priority = self.request.query_params.get('priority')
        
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read.lower() == 'true')
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        if priority:
            queryset = queryset.filter(priority=priority)
        
        return queryset.order_by('-created_at')


class NotificationMarkReadView(generics.GenericAPIView):
    """
    Vista para marcar notificaciones como leídas
    """
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationMarkReadSerializer
    
    def post(self, request):
        """
        Marcar notificaciones específicas como leídas
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data['notification_ids']
        user = request.user
        
        # Actualizar notificaciones del usuario
        updated_count = Notification.objects.filter(
            id__in=notification_ids,
            user=user,
            is_read=False
        ).update(is_read=True)
        
        return Response({
            'message': f'{updated_count} notificaciones marcadas como leídas',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    """
    Marcar todas las notificaciones del usuario como leídas
    """
    user = request.user
    updated_count = Notification.objects.filter(
        user=user,
        is_read=False,
        is_active=True
    ).update(is_read=True)
    
    return Response({
        'message': f'Todas las notificaciones marcadas como leídas',
        'updated_count': updated_count
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def navigation_stats(request):
    """
    Obtener estadísticas de navegación del usuario
    """
    user = request.user
    
    # Estadísticas básicas
    total_notifications = Notification.objects.filter(user=user, is_active=True).count()
    unread_notifications = Notification.objects.filter(
        user=user, is_active=True, is_read=False
    ).count()
    
    # Notificaciones por tipo
    notifications_by_type = {}
    for choice in Notification.NOTIFICATION_TYPES:
        type_key = choice[0]
        count = Notification.objects.filter(
            user=user, is_active=True, notification_type=type_key
        ).count()
        notifications_by_type[type_key] = count
    
    # Sección actual
    current_section = None
    try:
        user_nav = UserNavigation.objects.get(user=user)
        current_section = user_nav.current_section.name
    except UserNavigation.DoesNotExist:
        pass
    
    return Response({
        'total_notifications': total_notifications,
        'unread_notifications': unread_notifications,
        'notifications_by_type': notifications_by_type,
        'current_section': current_section,
        'user_email': user.email
    }, status=status.HTTP_200_OK)

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404, render
from django.db.models import Q, Count, Max, Prefetch
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import timedelta
import random
from .models import Conversation, Message, MessageRead, MessageReaction, UserStatus
from .serializers import (
    ConversationListSerializer, ConversationDetailSerializer, ConversationCreateSerializer,
    MessageSerializer, MessageCreateSerializer,
    MessageReactionSerializer, UserStatusSerializer, MessageStatsSerializer,
    BulkMessageActionSerializer
)

User = get_user_model()


# Vista para renderizar el chat (para testing)
def chat_view(request, conversation_id):
    """Vista para mostrar la interfaz de chat"""
    if not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())
    
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Verificar que el usuario puede acceder a esta conversación
    if not conversation.participants.filter(id=request.user.id).exists():
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("No tienes acceso a esta conversación")
    
    return render(request, 'messaging/chat.html', {
        'conversation': conversation
    })


class MessagePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ConversationListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear conversaciones
    """
    permission_classes = [IsAuthenticated]
    pagination_class = MessagePagination
    
    def get_queryset(self):
        user = self.request.user
        queryset = Conversation.objects.filter(
            participants=user,
            is_active=True
        ).prefetch_related(
            'participants',
            'created_by',
            Prefetch('messages', queryset=Message.objects.filter(is_deleted=False).order_by('-created_at')[:1])
        ).annotate(
            unread_count=Count('messages', filter=Q(messages__is_read=False, messages__is_deleted=False))
        ).distinct()
        
        # Filtros
        conversation_type = self.request.query_params.get('type')
        if conversation_type:
            queryset = queryset.filter(conversation_type=conversation_type)
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(participants__first_name__icontains=search) |
                Q(participants__last_name__icontains=search) |
                Q(participants__email__icontains=search)
            ).distinct()
        
        return queryset.order_by('-updated_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ConversationCreateSerializer
        return ConversationListSerializer


class ConversationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar una conversación específica
    """
    serializer_class = ConversationDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            'participants',
            'created_by',
            Prefetch(
                'messages',
                queryset=Message.objects.filter(is_deleted=False).select_related('sender', 'reply_to').prefetch_related('reactions', 'read_by').order_by('-created_at')
            )
        ).annotate(
            unread_count=Count('messages', filter=Q(messages__is_read=False, messages__is_deleted=False))
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Marcar mensajes como leídos
        unread_messages = instance.messages.filter(
            is_read=False,
            is_deleted=False
        ).exclude(sender=request.user)
        
        for message in unread_messages:
            message.mark_as_read()
            MessageRead.objects.get_or_create(
                message=message,
                user=request.user
            )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MessageListCreateView(generics.ListCreateAPIView):
    """
    Vista para listar y crear mensajes en una conversación
    """
    permission_classes = [IsAuthenticated]
    pagination_class = MessagePagination
    
    def get_queryset(self):
        conversation_id = self.kwargs['conversation_id']
        
        # Verificar que el usuario participa en la conversación
        conversation = Conversation.objects.filter(
            id=conversation_id,
            participants=self.request.user
        ).first()
        
        if not conversation:
            return Message.objects.none()
        
        return Message.objects.filter(
            conversation_id=conversation_id,
            is_deleted=False
        ).select_related('sender', 'reply_to').prefetch_related(
            'reactions__user',
            'read_by__user'
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MessageCreateSerializer
        return MessageSerializer
    
    def perform_create(self, serializer):
        conversation_id = self.kwargs['conversation_id']
        conversation = Conversation.objects.get(
            id=conversation_id,
            participants=self.request.user
        )
        serializer.save(conversation=conversation, sender=self.request.user)


class MessageDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Vista para obtener, actualizar y eliminar un mensaje específico
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Message.objects.filter(
            conversation__participants=self.request.user,
            is_deleted=False
        ).select_related('sender', 'reply_to').prefetch_related(
            'reactions__user',
            'read_by__user'
        )
    
    def perform_destroy(self, instance):
        # Soft delete
        instance.is_deleted = True
        instance.save()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def message_stats(request):
    """
    Obtiene estadísticas de mensajería para el usuario actual
    """
    user = request.user
    
    # Estadísticas básicas
    total_conversations = Conversation.objects.filter(participants=user, is_active=True).count()
    total_messages = Message.objects.filter(
        conversation__participants=user,
        is_deleted=False
    ).count()
    unread_messages = Message.objects.filter(
        conversation__participants=user,
        is_read=False,
        is_deleted=False
    ).exclude(sender=user).count()
    active_conversations = Conversation.objects.filter(
        participants=user,
        is_active=True,
        messages__created_at__gte=timezone.now() - timedelta(days=7)
    ).distinct().count()
    
    # Mensajes por período
    today = timezone.now().date()
    messages_today = Message.objects.filter(
        conversation__participants=user,
        is_deleted=False,
        created_at__date=today
    ).count()
    
    week_ago = timezone.now() - timedelta(days=7)
    messages_this_week = Message.objects.filter(
        conversation__participants=user,
        is_deleted=False,
        created_at__gte=week_ago
    ).count()
    
    # Conversaciones por tipo
    conversations_by_type = dict(
        Conversation.objects.filter(participants=user, is_active=True)
        .values('conversation_type')
        .annotate(count=Count('id'))
        .values_list('conversation_type', 'count')
    )
    
    # Top contactos (usuarios con más mensajes)
    top_contacts = list(
        User.objects.filter(
            sent_messages__conversation__participants=user,
            sent_messages__is_deleted=False
        ).exclude(id=user.id)
        .annotate(message_count=Count('sent_messages'))
        .order_by('-message_count')[:5]
        .values('id', 'first_name', 'last_name', 'email', 'message_count')
    )
    
    stats_data = {
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'unread_messages': unread_messages,
        'active_conversations': active_conversations,
        'messages_today': messages_today,
        'messages_this_week': messages_this_week,
        'conversations_by_type': conversations_by_type,
        'top_contacts': top_contacts
    }
    
    serializer = MessageStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_reaction(request, message_id):
    """
    Agregar o cambiar reacción a un mensaje
    """
    try:
        message = Message.objects.get(
            id=message_id,
            conversation__participants=request.user,
            is_deleted=False
        )
    except Message.DoesNotExist:
        return Response(
            {'error': 'Mensaje no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    reaction_type = request.data.get('reaction_type')
    if not reaction_type or reaction_type not in dict(MessageReaction.REACTION_TYPES):
        return Response(
            {'error': 'Tipo de reacción inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Crear o actualizar reacción
    reaction, created = MessageReaction.objects.update_or_create(
        message=message,
        user=request.user,
        defaults={'reaction_type': reaction_type}
    )
    
    return Response({
        'message': 'Reacción agregada' if created else 'Reacción actualizada',
        'reaction': {
            'id': reaction.id,
            'reaction_type': reaction.reaction_type,
            'reaction_emoji': reaction.get_reaction_type_display()
        }
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_reaction(request, message_id):
    """
    Eliminar reacción de un mensaje
    """
    try:
        reaction = MessageReaction.objects.get(
            message_id=message_id,
            user=request.user,
            message__conversation__participants=request.user
        )
        reaction.delete()
        return Response({'message': 'Reacción eliminada'})
    except MessageReaction.DoesNotExist:
        return Response(
            {'error': 'Reacción no encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_message_actions(request):
    """
    Realizar acciones en lote sobre mensajes
    """
    serializer = BulkMessageActionSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    message_ids = serializer.validated_data['message_ids']
    action = serializer.validated_data['action']
    
    messages = Message.objects.filter(
        id__in=message_ids,
        conversation__participants=request.user
    )
    
    if action == 'mark_read':
        messages.update(is_read=True, read_at=timezone.now())
        # Crear registros de lectura
        for message in messages:
            MessageRead.objects.get_or_create(
                message=message,
                user=request.user
            )
    elif action == 'mark_unread':
        messages.update(is_read=False, read_at=None)
        MessageRead.objects.filter(
            message__in=messages,
            user=request.user
        ).delete()
    elif action == 'delete':
        messages.update(is_deleted=True)
    
    return Response({
        'message': f'Acción "{action}" aplicada a {messages.count()} mensajes',
        'affected_count': messages.count()
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_messages(request):
    """
    Buscar mensajes en todas las conversaciones del usuario
    """
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({'error': 'Parámetro de búsqueda requerido'}, status=status.HTTP_400_BAD_REQUEST)
    
    messages = Message.objects.filter(
        conversation__participants=request.user,
        is_deleted=False,
        content__icontains=query
    ).select_related('sender', 'conversation').order_by('-created_at')
    
    # Filtros adicionales
    conversation_id = request.query_params.get('conversation_id')
    if conversation_id:
        messages = messages.filter(conversation_id=conversation_id)
    
    message_type = request.query_params.get('type')
    if message_type:
        messages = messages.filter(message_type=message_type)
    
    # Paginación
    paginator = MessagePagination()
    page = paginator.paginate_queryset(messages, request)
    
    serializer = MessageSerializer(page, many=True, context={'request': request})
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def user_status(request):
    """
    Obtener o actualizar el estado del usuario
    """
    user_status_obj, created = UserStatus.objects.get_or_create(
        user=request.user,
        defaults={'status': 'online'}
    )
    
    if request.method == 'GET':
        serializer = UserStatusSerializer(user_status_obj)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = UserStatusSerializer(user_status_obj, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def online_users(request):
    """
    Obtener lista de usuarios en línea
    """
    online_users = UserStatus.objects.filter(
        status='online',
        last_seen__gte=timezone.now() - timedelta(minutes=5)
    ).select_related('user')
    
    serializer = UserStatusSerializer(online_users, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_mock_messages(request):
    """
    Generar mensajes de prueba para desarrollo
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Solo el personal puede generar datos de prueba'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    count = int(request.data.get('count', 50))
    
    # Obtener usuarios existentes
    users = list(User.objects.all())
    if len(users) < 2:
        return Response(
            {'error': 'Se necesitan al menos 2 usuarios para generar conversaciones'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Crear conversaciones de prueba
    conversation_types = ['direct', 'group', 'support']
    sample_titles = [
        'Proyecto Inmobiliario Centro',
        'Consulta sobre Apartamento',
        'Negociación Casa Familiar',
        'Soporte Técnico',
        'Reunión Equipo Ventas',
        'Cliente Potencial',
        'Documentación Contrato'
    ]
    
    sample_messages = [
        'Hola, ¿cómo estás?',
        'Necesito información sobre la propiedad',
        '¿Podemos agendar una cita?',
        'El cliente está interesado en la propuesta',
        'Adjunto los documentos solicitados',
        'Perfecto, quedamos así entonces',
        'Gracias por la información',
        'Te confirmo la reunión para mañana',
        '¿Has revisado el contrato?',
        'Todo listo para la firma'
    ]
    
    conversations_created = 0
    messages_created = 0
    
    for _ in range(min(count // 10, 20)):  # Crear hasta 20 conversaciones
        # Seleccionar participantes aleatorios
        participants = random.sample(users, random.randint(2, min(5, len(users))))
        
        conversation = Conversation.objects.create(
            title=random.choice(sample_titles),
            conversation_type=random.choice(conversation_types),
            created_by=random.choice(participants)
        )
        conversation.participants.set(participants)
        conversations_created += 1
        
        # Crear mensajes para esta conversación
        num_messages = random.randint(3, 15)
        for _ in range(num_messages):
            Message.objects.create(
                conversation=conversation,
                sender=random.choice(participants),
                message_type='text',
                content=random.choice(sample_messages),
                is_read=random.choice([True, False])
            )
            messages_created += 1
    
    return Response({
        'message': 'Datos de prueba generados exitosamente',
        'conversations_created': conversations_created,
        'messages_created': messages_created
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_user_messages(request):
    """
    Eliminar todos los mensajes del usuario actual (solo para desarrollo)
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Solo el personal puede eliminar datos de prueba'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Eliminar conversaciones donde el usuario es el único participante
    user_conversations = Conversation.objects.filter(participants=request.user)
    deleted_conversations = 0
    deleted_messages = 0
    
    for conversation in user_conversations:
        if conversation.participants.count() == 1:
            deleted_messages += conversation.messages.count()
            conversation.delete()
            deleted_conversations += 1
        else:
            # Solo eliminar mensajes del usuario
            user_messages = conversation.messages.filter(sender=request.user)
            deleted_messages += user_messages.count()
            user_messages.delete()
            conversation.participants.remove(request.user)
    
    return Response({
        'message': 'Datos del usuario eliminados',
        'deleted_conversations': deleted_conversations,
        'deleted_messages': deleted_messages
    })
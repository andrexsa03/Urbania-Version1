"""
Signals para notificaciones en tiempo real
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Message, MessageReaction


@receiver(post_save, sender=Message)
def message_created(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta cuando se crea un nuevo mensaje
    Envía notificaciones a usuarios que no están en el chat activo
    """
    if created and not instance.is_deleted:
        channel_layer = get_channel_layer()
        
        # Obtener participantes de la conversación excepto el remitente
        participants = instance.conversation.participants.exclude(id=instance.sender.id)
        
        # Preparar datos del mensaje para la notificación
        message_data = {
            'id': instance.id,
            'content': instance.content[:100] + '...' if len(instance.content) > 100 else instance.content,
            'sender': {
                'email': instance.sender.email,
                'name': instance.sender.get_full_name()
            },
            'conversation': {
                'id': instance.conversation.id,
                'title': instance.conversation.title or f'Chat con {instance.sender.get_full_name()}'
            },
            'created_at': instance.created_at.isoformat()
        }
        
        # Enviar notificación a cada participante
        for participant in participants:
            notification_data = {
                'type': 'new_message',
                'title': f'Nuevo mensaje de {instance.sender.get_full_name()}',
                'message': message_data,
                'timestamp': instance.created_at.isoformat()
            }
            
            # Enviar al grupo personal del usuario para notificaciones
            async_to_sync(channel_layer.group_send)(
                f'user_{participant.id}',
                {
                    'type': 'notification',
                    'notification': notification_data
                }
            )


@receiver(post_save, sender=MessageReaction)
def reaction_created(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta cuando se crea o actualiza una reacción
    """
    if created:
        channel_layer = get_channel_layer()
        
        # Notificar al autor del mensaje original (si no es el mismo que reaccionó)
        if instance.message.sender != instance.user:
            notification_data = {
                'type': 'message_reaction',
                'title': f'{instance.user.get_full_name()} reaccionó a tu mensaje',
                'message': {
                    'id': instance.message.id,
                    'content': instance.message.content[:50] + '...' if len(instance.message.content) > 50 else instance.message.content,
                    'conversation_id': instance.message.conversation.id
                },
                'reaction': {
                    'type': instance.reaction_type,
                    'user': instance.user.get_full_name()
                },
                'timestamp': instance.created_at.isoformat()
            }
            
            # Enviar notificación al autor del mensaje
            async_to_sync(channel_layer.group_send)(
                f'user_{instance.message.sender.id}',
                {
                    'type': 'notification',
                    'notification': notification_data
                }
            )
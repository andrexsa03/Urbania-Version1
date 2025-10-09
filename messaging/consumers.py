"""
WebSocket consumers for real-time messaging
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Conversation, Message, UserStatus

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    Consumer para chat en tiempo real en conversaciones específicas
    """
    
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Verificar que el usuario puede acceder a esta conversación
        can_access = await self.can_access_conversation()
        if not can_access:
            await self.close()
            return
        
        # Unirse al grupo de la conversación
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Marcar mensajes como leídos
        await self.mark_messages_as_read()
        
        # Notificar que el usuario se conectó
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user': self.user.email,
                'message': f'{self.user.get_full_name()} se conectó'
            }
        )
    
    async def disconnect(self, close_code):
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Notificar que el usuario se desconectó
        if hasattr(self, 'user') and not self.user.is_anonymous:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user': self.user.email,
                    'message': f'{self.user.get_full_name()} se desconectó'
                }
            )
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type', 'message')
            
            if message_type == 'message':
                await self.handle_message(text_data_json)
            elif message_type == 'typing':
                await self.handle_typing(text_data_json)
            elif message_type == 'read_message':
                await self.handle_read_message(text_data_json)
            elif message_type == 'reaction':
                await self.handle_reaction(text_data_json)
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
    
    async def handle_message(self, data):
        content = data.get('content', '').strip()
        reply_to_id = data.get('reply_to')
        
        if not content:
            return
        
        # Crear el mensaje en la base de datos
        message = await self.create_message(content, reply_to_id)
        
        if message:
            # Enviar mensaje a todos en el grupo
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': await self.serialize_message(message)
                }
            )
    
    async def handle_typing(self, data):
        is_typing = data.get('is_typing', False)
        
        # Enviar indicador de escritura a otros usuarios
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user': self.user.email,
                'user_name': self.user.get_full_name(),
                'is_typing': is_typing
            }
        )
    
    async def handle_read_message(self, data):
        message_id = data.get('message_id')
        if message_id:
            await self.mark_message_as_read(message_id)
    
    async def handle_reaction(self, data):
        message_id = data.get('message_id')
        reaction_type = data.get('reaction_type')
        
        if message_id and reaction_type:
            reaction = await self.add_reaction(message_id, reaction_type)
            if reaction:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'message_reaction',
                        'message_id': message_id,
                        'user': self.user.email,
                        'reaction_type': reaction_type,
                        'action': 'add'
                    }
                )
    
    # Handlers para mensajes del grupo
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))
    
    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user': event['user'],
            'message': event['message']
        }))
    
    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user': event['user'],
            'message': event['message']
        }))
    
    async def typing_indicator(self, event):
        # No enviar el indicador al mismo usuario que está escribiendo
        if event['user'] != self.user.email:
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'user': event['user'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing']
            }))
    
    async def message_reaction(self, event):
        await self.send(text_data=json.dumps({
            'type': 'reaction',
            'message_id': event['message_id'],
            'user': event['user'],
            'reaction_type': event['reaction_type'],
            'action': event['action']
        }))
    
    # Métodos de base de datos
    @database_sync_to_async
    def can_access_conversation(self):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            return conversation.participants.filter(id=self.user.id).exists()
        except Conversation.DoesNotExist:
            return False
    
    @database_sync_to_async
    def create_message(self, content, reply_to_id=None):
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            
            reply_to = None
            if reply_to_id:
                try:
                    reply_to = Message.objects.get(id=reply_to_id, conversation=conversation)
                except Message.DoesNotExist:
                    pass
            
            message = Message.objects.create(
                conversation=conversation,
                sender=self.user,
                content=content,
                reply_to=reply_to
            )
            return message
        except Conversation.DoesNotExist:
            return None
    
    @database_sync_to_async
    def serialize_message(self, message):
        return {
            'id': message.id,
            'content': message.content,
            'sender': {
                'email': message.sender.email,
                'name': message.sender.get_full_name()
            },
            'reply_to': {
                'id': message.reply_to.id,
                'content': message.reply_to.content[:50] + '...' if len(message.reply_to.content) > 50 else message.reply_to.content,
                'sender': message.reply_to.sender.get_full_name()
            } if message.reply_to else None,
            'created_at': message.created_at.isoformat(),
            'is_read': False
        }
    
    @database_sync_to_async
    def mark_messages_as_read(self):
        from .models import MessageRead
        conversation = Conversation.objects.get(id=self.conversation_id)
        unread_messages = Message.objects.filter(
            conversation=conversation,
            is_deleted=False
        ).exclude(sender=self.user)
        
        for message in unread_messages:
            MessageRead.objects.get_or_create(
                message=message,
                user=self.user,
                defaults={'read_at': timezone.now()}
            )
    
    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        from .models import MessageRead
        try:
            message = Message.objects.get(id=message_id, conversation_id=self.conversation_id)
            MessageRead.objects.get_or_create(
                message=message,
                user=self.user,
                defaults={'read_at': timezone.now()}
            )
        except Message.DoesNotExist:
            pass
    
    @database_sync_to_async
    def add_reaction(self, message_id, reaction_type):
        from .models import MessageReaction
        try:
            message = Message.objects.get(id=message_id, conversation_id=self.conversation_id)
            reaction, created = MessageReaction.objects.get_or_create(
                message=message,
                user=self.user,
                defaults={'reaction_type': reaction_type}
            )
            if not created:
                reaction.reaction_type = reaction_type
                reaction.save()
            return reaction
        except Message.DoesNotExist:
            return None


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Consumer para notificaciones generales del usuario
    """
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.user_group_name = f'user_{self.user.id}'
        
        # Unirse al grupo personal del usuario
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'user_group_name'):
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        # Este consumer principalmente recibe notificaciones, no procesa mensajes entrantes
        pass
    
    async def notification(self, event):
        """Enviar notificación al usuario"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))


class UserStatusConsumer(AsyncWebsocketConsumer):
    """
    Consumer para gestionar el estado de conexión de usuarios
    """
    
    async def connect(self):
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        # Grupo global para estado de usuarios
        self.status_group_name = 'user_status'
        
        await self.channel_layer.group_add(
            self.status_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Actualizar estado a online
        await self.update_user_status('online')
        
        # Notificar a otros usuarios
        await self.broadcast_status_change('online')
    
    async def disconnect(self, close_code):
        # Actualizar estado a offline
        await self.update_user_status('offline')
        
        # Notificar a otros usuarios
        await self.broadcast_status_change('offline')
        
        await self.channel_layer.group_discard(
            self.status_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            status = data.get('status')
            custom_message = data.get('custom_message', '')
            
            if status in ['online', 'away', 'busy', 'offline']:
                await self.update_user_status(status, custom_message)
                await self.broadcast_status_change(status, custom_message)
                
        except json.JSONDecodeError:
            pass
    
    async def status_update(self, event):
        """Recibir actualizaciones de estado de otros usuarios"""
        if event['user_id'] != self.user.id:  # No enviar el propio estado
            await self.send(text_data=json.dumps({
                'type': 'status_update',
                'user_id': event['user_id'],
                'user_email': event['user_email'],
                'user_name': event['user_name'],
                'status': event['status'],
                'custom_message': event.get('custom_message', ''),
                'last_seen': event.get('last_seen')
            }))
    
    @database_sync_to_async
    def update_user_status(self, status, custom_message=''):
        user_status, created = UserStatus.objects.get_or_create(
            user=self.user,
            defaults={
                'status': status,
                'custom_message': custom_message,
                'last_seen': timezone.now()
            }
        )
        if not created:
            user_status.status = status
            user_status.custom_message = custom_message
            user_status.last_seen = timezone.now()
            user_status.save()
        return user_status
    
    async def broadcast_status_change(self, status, custom_message=''):
        """Notificar cambio de estado a todos los usuarios conectados"""
        await self.channel_layer.group_send(
            self.status_group_name,
            {
                'type': 'status_update',
                'user_id': self.user.id,
                'user_email': self.user.email,
                'user_name': self.user.get_full_name(),
                'status': status,
                'custom_message': custom_message,
                'last_seen': timezone.now().isoformat()
            }
        )
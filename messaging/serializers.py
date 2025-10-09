from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Conversation, Message, MessageRead, MessageReaction, UserStatus

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para información de usuario"""
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    avatar = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name', 'avatar']
    
    def get_avatar(self, obj):
        # Placeholder para avatar - se puede implementar más tarde
        return f"https://ui-avatars.com/api/?name={obj.get_full_name()}&background=random"


class UserStatusSerializer(serializers.ModelSerializer):
    """Serializer para el estado de usuario"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = UserStatus
        fields = ['user', 'status', 'last_seen', 'custom_message', 'is_online']


class MessageReactionSerializer(serializers.ModelSerializer):
    """Serializer para reacciones a mensajes"""
    user = UserBasicSerializer(read_only=True)
    reaction_emoji = serializers.CharField(source='get_reaction_type_display', read_only=True)
    
    class Meta:
        model = MessageReaction
        fields = ['id', 'user', 'reaction_type', 'reaction_emoji', 'created_at']


class MessageReadSerializer(serializers.ModelSerializer):
    """Serializer para lecturas de mensajes"""
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = MessageRead
        fields = ['user', 'read_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer para mensajes"""
    sender = UserBasicSerializer(read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    read_by = MessageReadSerializer(many=True, read_only=True)
    reply_to_message = serializers.SerializerMethodField()
    attachment_name = serializers.CharField(read_only=True)
    attachment_url = serializers.SerializerMethodField()
    time_ago = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'sender', 'message_type', 'content', 'attachment', 
            'attachment_name', 'attachment_url', 'is_read', 'reply_to',
            'reply_to_message', 'reactions', 'read_by', 'created_at', 
            'updated_at', 'read_at', 'time_ago'
        ]
        read_only_fields = ['sender', 'created_at', 'updated_at', 'read_at']
    
    def get_reply_to_message(self, obj):
        if obj.reply_to:
            return {
                'id': obj.reply_to.id,
                'sender': obj.reply_to.sender.get_full_name(),
                'content': obj.reply_to.content[:100] + '...' if len(obj.reply_to.content) > 100 else obj.reply_to.content,
                'message_type': obj.reply_to.message_type
            }
        return None
    
    def get_attachment_url(self, obj):
        if obj.attachment:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.attachment.url)
            return obj.attachment.url
        return None
    
    def get_time_ago(self, obj):
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days > 0:
            return f"hace {diff.days} día{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"hace {hours} hora{'s' if hours > 1 else ''}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"hace {minutes} minuto{'s' if minutes > 1 else ''}"
        else:
            return "hace un momento"


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear mensajes"""
    
    class Meta:
        model = Message
        fields = ['conversation', 'message_type', 'content', 'attachment', 'reply_to']
    
    def validate(self, data):
        if data['message_type'] == 'text' and not data.get('content'):
            raise serializers.ValidationError("El contenido es requerido para mensajes de texto")
        
        if data['message_type'] in ['file', 'image'] and not data.get('attachment'):
            raise serializers.ValidationError("El archivo adjunto es requerido para este tipo de mensaje")
        
        return data
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        return super().create(validated_data)


class ConversationListSerializer(serializers.ModelSerializer):
    """Serializer para lista de conversaciones"""
    participants = UserBasicSerializer(many=True, read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.IntegerField(read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'conversation_type', 'participants', 'created_by',
            'last_message', 'unread_count', 'participant_count', 'created_at',
            'updated_at', 'is_active'
        ]
    
    def get_last_message(self, obj):
        last_msg = obj.last_message
        if last_msg:
            return {
                'id': last_msg.id,
                'sender': last_msg.sender.get_full_name(),
                'content': last_msg.content[:100] + '...' if len(last_msg.content) > 100 else last_msg.content,
                'message_type': last_msg.message_type,
                'created_at': last_msg.created_at,
                'is_read': last_msg.is_read
            }
        return None
    
    def get_participant_count(self, obj):
        return obj.participants.count()


class ConversationDetailSerializer(serializers.ModelSerializer):
    """Serializer detallado para conversaciones"""
    participants = UserBasicSerializer(many=True, read_only=True)
    created_by = UserBasicSerializer(read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    unread_count = serializers.IntegerField(read_only=True)
    participant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'conversation_type', 'participants', 'created_by',
            'messages', 'unread_count', 'participant_count', 'created_at',
            'updated_at', 'is_active'
        ]
    
    def get_participant_count(self, obj):
        return obj.participants.count()


class ConversationCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear conversaciones"""
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=True
    )
    
    class Meta:
        model = Conversation
        fields = ['title', 'conversation_type', 'participant_ids']
    
    def validate_participant_ids(self, value):
        if not value:
            raise serializers.ValidationError("Debe especificar al menos un participante")
        
        # Verificar que los usuarios existen
        existing_users = User.objects.filter(id__in=value).count()
        if existing_users != len(value):
            raise serializers.ValidationError("Algunos usuarios especificados no existen")
        
        return value
    
    def create(self, validated_data):
        participant_ids = validated_data.pop('participant_ids')
        validated_data['created_by'] = self.context['request'].user
        
        conversation = super().create(validated_data)
        
        # Agregar participantes
        participants = User.objects.filter(id__in=participant_ids)
        conversation.participants.set(participants)
        
        # Agregar al creador como participante si no está incluido
        if self.context['request'].user not in participants:
            conversation.participants.add(self.context['request'].user)
        
        return conversation


class MessageStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de mensajes"""
    total_conversations = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    unread_messages = serializers.IntegerField()
    active_conversations = serializers.IntegerField()
    messages_today = serializers.IntegerField()
    messages_this_week = serializers.IntegerField()
    conversations_by_type = serializers.DictField()
    top_contacts = serializers.ListField()


class BulkMessageActionSerializer(serializers.Serializer):
    """Serializer para acciones en lote sobre mensajes"""
    message_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )
    action = serializers.ChoiceField(
        choices=['mark_read', 'mark_unread', 'delete'],
        required=True
    )
    
    def validate_message_ids(self, value):
        if not value:
            raise serializers.ValidationError("Debe especificar al menos un mensaje")
        
        # Verificar que los mensajes existen y pertenecen al usuario
        user = self.context['request'].user
        existing_messages = Message.objects.filter(
            id__in=value,
            conversation__participants=user
        ).count()
        
        if existing_messages != len(value):
            raise serializers.ValidationError("Algunos mensajes no existen o no tienes acceso a ellos")
        
        return value
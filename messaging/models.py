from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import FileExtensionValidator

User = get_user_model()


class Conversation(models.Model):
    """
    Modelo para representar una conversación entre usuarios
    """
    CONVERSATION_TYPES = [
        ('direct', 'Conversación Directa'),
        ('group', 'Conversación Grupal'),
        ('support', 'Soporte Técnico'),
        ('announcement', 'Anuncio'),
    ]
    
    title = models.CharField(max_length=200, blank=True, null=True, verbose_name='Título')
    conversation_type = models.CharField(
        max_length=20, 
        choices=CONVERSATION_TYPES, 
        default='direct',
        verbose_name='Tipo de Conversación'
    )
    participants = models.ManyToManyField(
        User, 
        related_name='conversations',
        verbose_name='Participantes'
    )
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='created_conversations',
        verbose_name='Creado por'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    
    class Meta:
        verbose_name = 'Conversación'
        verbose_name_plural = 'Conversaciones'
        ordering = ['-updated_at']
    
    def __str__(self):
        if self.title:
            return self.title
        elif self.conversation_type == 'direct':
            participants = list(self.participants.all()[:2])
            if len(participants) == 2:
                return f"Conversación entre {participants[0].get_full_name()} y {participants[1].get_full_name()}"
        return f"Conversación #{self.id}"
    
    @property
    def last_message(self):
        """Obtiene el último mensaje de la conversación"""
        return self.messages.filter(is_deleted=False).first()
    
    @property
    def unread_count(self):
        """Cuenta los mensajes no leídos en la conversación"""
        return self.messages.filter(is_read=False, is_deleted=False).count()


class Message(models.Model):
    """
    Modelo para representar un mensaje dentro de una conversación
    """
    MESSAGE_TYPES = [
        ('text', 'Texto'),
        ('file', 'Archivo'),
        ('image', 'Imagen'),
        ('system', 'Sistema'),
    ]
    
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages',
        verbose_name='Conversación'
    )
    sender = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='sent_messages',
        verbose_name='Remitente'
    )
    message_type = models.CharField(
        max_length=20, 
        choices=MESSAGE_TYPES, 
        default='text',
        verbose_name='Tipo de Mensaje'
    )
    content = models.TextField(verbose_name='Contenido')
    attachment = models.FileField(
        upload_to='messaging/attachments/%Y/%m/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif'])],
        verbose_name='Archivo adjunto'
    )
    is_read = models.BooleanField(default=False, verbose_name='Leído')
    is_deleted = models.BooleanField(default=False, verbose_name='Eliminado')
    reply_to = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        blank=True, 
        null=True,
        related_name='replies',
        verbose_name='Respuesta a'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de envío')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última actualización')
    read_at = models.DateTimeField(blank=True, null=True, verbose_name='Fecha de lectura')
    
    class Meta:
        verbose_name = 'Mensaje'
        verbose_name_plural = 'Mensajes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Mensaje de {self.sender.get_full_name()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    def mark_as_read(self):
        """Marca el mensaje como leído"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def attachment_name(self):
        """Obtiene el nombre del archivo adjunto"""
        if self.attachment:
            return self.attachment.name.split('/')[-1]
        return None


class MessageRead(models.Model):
    """
    Modelo para rastrear qué usuarios han leído qué mensajes
    """
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='read_by',
        verbose_name='Mensaje'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='read_messages',
        verbose_name='Usuario'
    )
    read_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de lectura')
    
    class Meta:
        verbose_name = 'Lectura de Mensaje'
        verbose_name_plural = 'Lecturas de Mensajes'
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} leyó mensaje #{self.message.id}"


class MessageReaction(models.Model):
    """
    Modelo para representar reacciones a mensajes
    """
    REACTION_TYPES = [
        ('like', '👍'),
        ('love', '❤️'),
        ('laugh', '😂'),
        ('wow', '😮'),
        ('sad', '😢'),
        ('angry', '😠'),
    ]
    
    message = models.ForeignKey(
        Message, 
        on_delete=models.CASCADE, 
        related_name='reactions',
        verbose_name='Mensaje'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='message_reactions',
        verbose_name='Usuario'
    )
    reaction_type = models.CharField(
        max_length=10, 
        choices=REACTION_TYPES,
        verbose_name='Tipo de Reacción'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de reacción')
    
    class Meta:
        verbose_name = 'Reacción a Mensaje'
        verbose_name_plural = 'Reacciones a Mensajes'
        unique_together = ['message', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name()} reaccionó {self.get_reaction_type_display()} al mensaje #{self.message.id}"


class UserStatus(models.Model):
    """
    Modelo para rastrear el estado de conexión de los usuarios
    """
    STATUS_CHOICES = [
        ('online', 'En línea'),
        ('away', 'Ausente'),
        ('busy', 'Ocupado'),
        ('offline', 'Desconectado'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='messaging_status',
        verbose_name='Usuario'
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='offline',
        verbose_name='Estado'
    )
    last_seen = models.DateTimeField(auto_now=True, verbose_name='Última vez visto')
    custom_message = models.CharField(
        max_length=100, 
        blank=True, 
        null=True,
        verbose_name='Mensaje personalizado'
    )
    
    class Meta:
        verbose_name = 'Estado de Usuario'
        verbose_name_plural = 'Estados de Usuarios'
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_status_display()}"
    
    @property
    def is_online(self):
        """Verifica si el usuario está en línea"""
        return self.status == 'online'
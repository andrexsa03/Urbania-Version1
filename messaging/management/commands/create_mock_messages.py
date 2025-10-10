from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from messaging.models import Conversation, Message, UserStatus
import random
from faker import Faker

User = get_user_model()
fake = Faker('es_ES')


class Command(BaseCommand):
    help = 'Crea conversaciones y mensajes de prueba para el sistema de mensajería'

    def add_arguments(self, parser):
        parser.add_argument(
            '--conversations',
            type=int,
            default=10,
            help='Número de conversaciones a crear (default: 10)'
        )
        parser.add_argument(
            '--messages-per-conversation',
            type=int,
            default=15,
            help='Número promedio de mensajes por conversación (default: 15)'
        )
        parser.add_argument(
            '--user-email',
            type=str,
            help='Email del usuario para crear conversaciones (opcional)'
        )

    def handle(self, *args, **options):
        conversations_count = options['conversations']
        messages_per_conversation = options['messages_per_conversation']
        user_email = options.get('user_email')

        # Obtener usuarios existentes
        users = list(User.objects.all())
        if len(users) < 2:
            self.stdout.write(
                self.style.ERROR('Se necesitan al menos 2 usuarios para crear conversaciones')
            )
            return

        # Si se especifica un email, usarlo como usuario principal
        main_user = None
        if user_email:
            try:
                main_user = User.objects.get(email=user_email)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'Usuario con email {user_email} no encontrado. Usando usuarios aleatorios.')
                )

        # Crear estados de usuario para todos los usuarios
        for user in users:
            UserStatus.objects.get_or_create(
                user=user,
                defaults={
                    'status': random.choice(['online', 'away', 'busy', 'offline']),
                    'custom_message': fake.sentence(nb_words=4) if random.choice([True, False]) else None
                }
            )

        # Tipos de conversación y títulos de ejemplo
        conversation_types = ['direct', 'group', 'support', 'announcement']
        conversation_titles = [
            'Proyecto Residencial Norte',
            'Consulta Apartamento Centro',
            'Negociación Casa Familiar',
            'Soporte Técnico - Plataforma',
            'Equipo Ventas - Reunión Semanal',
            'Cliente Premium - Seguimiento',
            'Documentación Legal',
            'Propuesta Comercial',
            'Revisión Contratos',
            'Coordinación Visitas'
        ]

        # Mensajes de ejemplo realistas para inmobiliaria
        sample_messages = [
            'Hola, ¿cómo estás? Espero que tengas un buen día.',
            'He revisado la propuesta y me parece interesante.',
            '¿Podríamos agendar una cita para esta semana?',
            'El cliente está muy interesado en la propiedad.',
            'Adjunto los documentos que me solicitaste.',
            'Perfecto, quedamos así entonces. Gracias por tu tiempo.',
            'Necesito que revises estos contratos cuando puedas.',
            'La visita de ayer fue muy exitosa.',
            '¿Has tenido noticias del banco sobre el préstamo?',
            'Te confirmo la reunión para mañana a las 10:00 AM.',
            'El precio me parece razonable, procedamos.',
            'Hay que coordinar la entrega de llaves.',
            'El cliente quiere hacer una contraoferta.',
            '¿Tienes disponibilidad para el viernes?',
            'Excelente trabajo en la presentación de ayer.',
            'Necesitamos actualizar la información de la propiedad.',
            'El avalúo ya está listo, te lo envío por correo.',
            '¿Cómo va el proceso de financiamiento?',
            'La documentación está completa y lista para firma.',
            'Gracias por tu ayuda con este cliente.'
        ]

        conversations_created = 0
        messages_created = 0

        self.stdout.write('Creando conversaciones y mensajes de prueba...')

        for i in range(conversations_count):
            # Determinar tipo de conversación
            conv_type = random.choice(conversation_types)
            
            # Seleccionar participantes
            if conv_type == 'direct':
                if main_user:
                    other_user = random.choice([u for u in users if u != main_user])
                    participants = [main_user, other_user]
                else:
                    participants = random.sample(users, 2)
                title = None  # Las conversaciones directas no necesitan título
            else:
                # Para conversaciones grupales, soporte o anuncios
                num_participants = random.randint(2, min(6, len(users)))
                if main_user:
                    available_users = [u for u in users if u != main_user]
                    if len(available_users) >= num_participants - 1:
                        other_participants = random.sample(available_users, num_participants - 1)
                        participants = [main_user] + other_participants
                    else:
                        participants = users[:num_participants]
                else:
                    participants = random.sample(users, min(num_participants, len(users)))
                title = random.choice(conversation_titles)

            # Crear conversación
            conversation = Conversation.objects.create(
                title=title,
                conversation_type=conv_type,
                created_by=participants[0]
            )
            conversation.participants.set(participants)
            conversations_created += 1

            # Crear mensajes para esta conversación
            num_messages = random.randint(
                max(3, messages_per_conversation - 5),
                messages_per_conversation + 5
            )
            
            for j in range(num_messages):
                sender = random.choice(participants)
                message_content = random.choice(sample_messages)
                
                # Ocasionalmente crear mensajes de sistema
                message_type = 'system' if random.random() < 0.05 else 'text'
                if message_type == 'system':
                    system_messages = [
                        f'{sender.get_full_name()} se unió a la conversación',
                        f'{sender.get_full_name()} cambió el título de la conversación',
                        'Se agregó un nuevo documento a la conversación',
                        'Se programó una reunión para mañana'
                    ]
                    message_content = random.choice(system_messages)

                # Crear mensaje
                message = Message.objects.create(
                    conversation=conversation,
                    sender=sender,
                    message_type=message_type,
                    content=message_content,
                    is_read=random.choice([True, False])
                )
                messages_created += 1

                # Ocasionalmente crear respuestas
                if j > 0 and random.random() < 0.2:
                    previous_messages = conversation.messages.all()[:j]
                    if previous_messages:
                        message.reply_to = random.choice(previous_messages)
                        message.save()

        # Mostrar estadísticas finales
        total_conversations = Conversation.objects.count()
        total_messages = Message.objects.count()
        
        # Estadísticas por tipo de conversación
        conv_stats = {}
        for conv_type, _ in Conversation.CONVERSATION_TYPES:
            count = Conversation.objects.filter(conversation_type=conv_type).count()
            conv_stats[conv_type] = count

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Datos de mensajería creados exitosamente!\n'
                f'📊 Estadísticas:\n'
                f'   • Conversaciones creadas: {conversations_created}\n'
                f'   • Mensajes creados: {messages_created}\n'
                f'   • Total conversaciones en BD: {total_conversations}\n'
                f'   • Total mensajes en BD: {total_messages}\n'
                f'\n📈 Conversaciones por tipo:'
            )
        )
        
        for conv_type, count in conv_stats.items():
            type_display = dict(Conversation.CONVERSATION_TYPES)[conv_type]
            self.stdout.write(f'   • {type_display}: {count}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎯 Los datos están listos para probar los endpoints de mensajería!'
            )
        )
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from contracts.models import Contract, ContractPayment, ContractDocument, ContractNote
from decimal import Decimal
import random
from datetime import date, timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Crea contratos ficticios para pruebas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=20,
            help='Número de contratos a crear (default: 20)'
        )
        parser.add_argument(
            '--user-email',
            type=str,
            default='admin@urbany.com',
            help='Email del usuario que creará los contratos'
        )

    def handle(self, *args, **options):
        count = options['count']
        user_email = options['user_email']
        
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Usuario con email {user_email} no encontrado')
            )
            return

        # Datos ficticios
        contract_types = ['sale', 'rent', 'lease', 'management']
        statuses = ['draft', 'pending', 'active', 'signed', 'completed', 'cancelled']
        priorities = ['low', 'medium', 'high', 'urgent']
        
        client_names = [
            'María García López', 'Juan Carlos Rodríguez', 'Ana Martínez Silva',
            'Pedro Sánchez Ruiz', 'Carmen Fernández Torres', 'Luis González Moreno',
            'Isabel Jiménez Castro', 'Miguel Ángel Herrera', 'Pilar Romero Vega',
            'Francisco Javier Díaz', 'Rosa María Álvarez', 'Antonio López Martín',
            'Dolores Muñoz Serrano', 'José Manuel Ortega', 'Concepción Ramos Gil'
        ]
        
        property_types = [
            'Apartamento', 'Casa', 'Chalet', 'Piso', 'Dúplex', 'Ático',
            'Estudio', 'Loft', 'Casa Rural', 'Local Comercial', 'Oficina'
        ]
        
        addresses = [
            'Calle Mayor 123, Madrid', 'Avenida de la Constitución 45, Sevilla',
            'Plaza del Carmen 12, Valencia', 'Calle Gran Vía 78, Barcelona',
            'Paseo de la Castellana 234, Madrid', 'Calle Sierpes 56, Sevilla',
            'Avenida del Puerto 89, Valencia', 'Rambla Catalunya 167, Barcelona',
            'Calle Alcalá 345, Madrid', 'Calle Betis 23, Sevilla'
        ]

        created_contracts = []
        
        for i in range(count):
            # Fechas aleatorias
            start_date = date.today() + timedelta(days=random.randint(-365, 365))
            end_date = start_date + timedelta(days=random.randint(30, 1095))
            signed_date = None
            
            status = random.choice(statuses)
            if status in ['signed', 'completed']:
                signed_date = start_date - timedelta(days=random.randint(1, 30))
            
            # Valores monetarios
            contract_value = Decimal(str(random.randint(50000, 500000)))
            commission_rate = Decimal(str(random.uniform(2.0, 8.0)))
            commission_amount = contract_value * (commission_rate / 100)
            
            contract = Contract.objects.create(
                title=f'Contrato {random.choice(contract_types).title()} - {random.choice(property_types)}',
                contract_type=random.choice(contract_types),
                status=status,
                priority=random.choice(priorities),
                client_name=random.choice(client_names),
                client_email=f'cliente{i+1}@email.com',
                client_phone=f'6{random.randint(10000000, 99999999)}',
                client_address=random.choice(addresses),
                agent=user,
                property_address=random.choice(addresses),
                property_type=random.choice(property_types),
                contract_value=contract_value,
                commission_rate=commission_rate,
                commission_amount=commission_amount,
                start_date=start_date,
                end_date=end_date,
                signed_date=signed_date,
                terms_and_conditions='Términos y condiciones estándar del contrato.',
                special_clauses='Cláusulas especiales según el tipo de contrato.',
                notes=f'Notas del contrato #{i+1}',
                created_by=user
            )
            
            created_contracts.append(contract)
            
            # Crear algunos pagos para contratos activos/firmados
            if status in ['active', 'signed', 'completed'] and random.choice([True, False]):
                payment_count = random.randint(1, 4)
                for j in range(payment_count):
                    payment_date = start_date + timedelta(days=j * 30)
                    payment_status = 'paid' if j == 0 else random.choice(['pending', 'paid', 'overdue'])
                    
                    ContractPayment.objects.create(
                        contract=contract,
                        payment_type=random.choice(['initial', 'monthly', 'final', 'commission']),
                        amount=Decimal(str(random.randint(1000, 10000))),
                        due_date=payment_date,
                        paid_date=payment_date if payment_status == 'paid' else None,
                        status=payment_status,
                        payment_method=random.choice(['transfer', 'check', 'cash', 'card']),
                        reference_number=f'PAY-{contract.id}-{j+1:03d}',
                        notes=f'Pago #{j+1} del contrato {contract.contract_number}'
                    )
            
            # Crear algunas notas
            if random.choice([True, False]):
                note_count = random.randint(1, 3)
                for j in range(note_count):
                    ContractNote.objects.create(
                        contract=contract,
                        note_type=random.choice(['general', 'meeting', 'call', 'email', 'document']),
                        title=f'Nota {j+1} - {contract.title}',
                        content=f'Contenido de la nota #{j+1} para el contrato {contract.contract_number}. Esta es una nota de ejemplo con información relevante.',
                        is_important=random.choice([True, False]),
                        created_by=user
                    )

        self.stdout.write(
            self.style.SUCCESS(
                f'Se crearon exitosamente {len(created_contracts)} contratos ficticios'
            )
        )
        
        # Mostrar estadísticas
        total_contracts = Contract.objects.count()
        self.stdout.write(f'Total de contratos en la base de datos: {total_contracts}')
        
        for contract_type in contract_types:
            count = Contract.objects.filter(contract_type=contract_type).count()
            self.stdout.write(f'  - {contract_type.title()}: {count}')
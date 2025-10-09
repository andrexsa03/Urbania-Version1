from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

User = get_user_model()


class Contract(models.Model):
    """Modelo principal para contratos inmobiliarios"""
    
    CONTRACT_TYPES = [
        ('sale', 'Compraventa'),
        ('rent', 'Arrendamiento'),
        ('lease', 'Arrendamiento Comercial'),
        ('management', 'Administración'),
        ('exclusive', 'Exclusividad'),
        ('option', 'Opción de Compra'),
    ]
    
    STATUS_CHOICES = [
        ('draft', 'Borrador'),
        ('pending', 'Pendiente'),
        ('active', 'Activo'),
        ('signed', 'Firmado'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
        ('expired', 'Vencido'),
        ('suspended', 'Suspendido'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    # Información básica
    contract_number = models.CharField(max_length=50, unique=True, verbose_name='Número de Contrato')
    title = models.CharField(max_length=200, verbose_name='Título del Contrato')
    contract_type = models.CharField(max_length=20, choices=CONTRACT_TYPES, verbose_name='Tipo de Contrato')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Estado')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='Prioridad')
    
    # Partes del contrato
    client_name = models.CharField(max_length=200, verbose_name='Nombre del Cliente')
    client_email = models.EmailField(blank=True, verbose_name='Email del Cliente')
    client_phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono del Cliente')
    client_address = models.TextField(blank=True, verbose_name='Dirección del Cliente')
    
    # Agente responsable
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contracts', verbose_name='Agente Responsable')
    
    # Detalles del contrato
    property_address = models.TextField(verbose_name='Dirección de la Propiedad')
    property_type = models.CharField(max_length=100, blank=True, verbose_name='Tipo de Propiedad')
    contract_value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor del Contrato')
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('3.00'), verbose_name='Tasa de Comisión (%)')
    commission_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True, verbose_name='Monto de Comisión')
    
    # Fechas importantes
    start_date = models.DateField(verbose_name='Fecha de Inicio')
    end_date = models.DateField(blank=True, null=True, verbose_name='Fecha de Finalización')
    signed_date = models.DateField(blank=True, null=True, verbose_name='Fecha de Firma')
    
    # Términos y condiciones
    terms_and_conditions = models.TextField(blank=True, verbose_name='Términos y Condiciones')
    special_clauses = models.TextField(blank=True, verbose_name='Cláusulas Especiales')
    notes = models.TextField(blank=True, verbose_name='Notas Adicionales')
    
    # Documentos y archivos
    contract_file = models.CharField(max_length=255, blank=True, verbose_name='Archivo del Contrato')
    attachments = models.TextField(blank=True, verbose_name='Archivos Adjuntos')
    
    # Metadatos
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_contracts', verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Contrato'
        verbose_name_plural = 'Contratos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'contract_type']),
            models.Index(fields=['agent', 'status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"{self.contract_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Calcular comisión automáticamente
        if self.contract_value and self.commission_rate:
            self.commission_amount = (self.contract_value * self.commission_rate) / 100
        
        # Generar número de contrato si no existe
        if not self.contract_number:
            self.contract_number = self.generate_contract_number()
        
        super().save(*args, **kwargs)
    
    def generate_contract_number(self):
        """Genera un número único de contrato"""
        year = timezone.now().year
        count = Contract.objects.filter(created_at__year=year).count() + 1
        return f"CTR-{year}-{count:04d}"
    
    def get_status_color(self):
        """Retorna el color asociado al estado"""
        colors = {
            'draft': 'secondary',
            'pending': 'warning',
            'active': 'primary',
            'signed': 'success',
            'completed': 'info',
            'cancelled': 'danger',
            'expired': 'dark',
            'suspended': 'warning'
        }
        return colors.get(self.status, 'secondary')
    
    def get_priority_color(self):
        """Retorna el color asociado a la prioridad"""
        colors = {
            'low': 'success',
            'medium': 'info',
            'high': 'warning',
            'urgent': 'danger'
        }
        return colors.get(self.priority, 'info')
    
    def get_type_icon(self):
        """Retorna el icono asociado al tipo de contrato"""
        icons = {
            'sale': 'fas fa-home',
            'rent': 'fas fa-key',
            'lease': 'fas fa-building',
            'management': 'fas fa-cogs',
            'exclusive': 'fas fa-star',
            'option': 'fas fa-handshake'
        }
        return icons.get(self.contract_type, 'fas fa-file-contract')
    
    def is_expired(self):
        """Verifica si el contrato está vencido"""
        if self.end_date:
            return timezone.now().date() > self.end_date
        return False
    
    def days_until_expiry(self):
        """Calcula los días hasta el vencimiento"""
        if self.end_date:
            delta = self.end_date - timezone.now().date()
            return delta.days if delta.days > 0 else 0
        return None
    
    def get_duration_days(self):
        """Calcula la duración del contrato en días"""
        if self.end_date:
            return (self.end_date - self.start_date).days
        return None
    
    def get_progress_percentage(self):
        """Calcula el porcentaje de progreso del contrato"""
        if not self.end_date:
            return 0
        
        total_days = (self.end_date - self.start_date).days
        elapsed_days = (timezone.now().date() - self.start_date).days
        
        if total_days <= 0:
            return 100
        
        progress = (elapsed_days / total_days) * 100
        return max(0, min(100, progress))
    
    @classmethod
    def generate_mock_contracts(cls, user, count=20):
        """Genera contratos mock para pruebas"""
        contracts = []
        
        contract_titles = [
            'Venta Casa Residencial Los Pinos',
            'Arrendamiento Apartamento Centro',
            'Administración Edificio Comercial',
            'Exclusividad Lote Campestre',
            'Opción Compra Villa Premium',
            'Arrendamiento Local Comercial',
            'Venta Penthouse Vista Mar',
            'Administración Conjunto Cerrado',
            'Arrendamiento Oficina Ejecutiva',
            'Venta Finca Recreativa',
            'Exclusividad Proyecto Nuevo',
            'Arrendamiento Bodega Industrial',
            'Venta Apartamento Familiar',
            'Administración Centro Comercial',
            'Opción Compra Terreno Urbano'
        ]
        
        client_names = [
            'María González Pérez',
            'Carlos Rodríguez Silva',
            'Ana Martínez López',
            'Luis Fernando Castro',
            'Patricia Herrera Ruiz',
            'Jorge Alberto Morales',
            'Carmen Elena Vargas',
            'Roberto Jiménez Torres',
            'Lucía Fernández Díaz',
            'Miguel Ángel Sánchez',
            'Isabella Ramírez Cruz',
            'Andrés Felipe Gómez',
            'Valentina Ospina Mejía',
            'Santiago Restrepo Arias',
            'Camila Andrea Vega'
        ]
        
        property_addresses = [
            'Calle 85 #15-23, Chapinero, Bogotá',
            'Carrera 11 #93-45, Zona Rosa, Bogotá',
            'Avenida El Poblado #10-50, Medellín',
            'Calle 70 #5-25, La Candelaria, Bogotá',
            'Carrera 43A #14-20, El Poblado, Medellín',
            'Avenida Santander #25-10, Manizales',
            'Calle 116 #7-15, Usaquén, Bogotá',
            'Carrera 65 #8B-91, Laureles, Medellín',
            'Avenida Las Palmas Km 7, Rionegro',
            'Calle 127 #19A-40, Suba, Bogotá'
        ]
        
        property_types = [
            'Casa', 'Apartamento', 'Local Comercial', 'Oficina',
            'Bodega', 'Lote', 'Finca', 'Penthouse', 'Estudio'
        ]
        
        for i in range(count):
            start_date = timezone.now().date() - timedelta(days=random.randint(0, 365))
            end_date = start_date + timedelta(days=random.randint(30, 1095))  # 1 mes a 3 años
            
            contract = cls.objects.create(
                title=random.choice(contract_titles),
                contract_type=random.choice([choice[0] for choice in cls.CONTRACT_TYPES]),
                status=random.choice([choice[0] for choice in cls.STATUS_CHOICES]),
                priority=random.choice([choice[0] for choice in cls.PRIORITY_CHOICES]),
                client_name=random.choice(client_names),
                client_email=f"{random.choice(client_names).lower().replace(' ', '.')}@email.com",
                client_phone=f"300{random.randint(1000000, 9999999)}",
                client_address=random.choice(property_addresses),
                agent=user,
                property_address=random.choice(property_addresses),
                property_type=random.choice(property_types),
                contract_value=Decimal(str(random.randint(50000000, 2000000000))),  # 50M a 2B COP
                commission_rate=Decimal(str(random.uniform(2.0, 6.0))),
                start_date=start_date,
                end_date=end_date,
                signed_date=start_date + timedelta(days=random.randint(0, 30)) if random.choice([True, False]) else None,
                terms_and_conditions=f"Contrato de {random.choice(['compraventa', 'arrendamiento', 'administración'])} con términos estándar del mercado inmobiliario.",
                special_clauses=f"Cláusula especial {i+1}: Condiciones particulares acordadas entre las partes.",
                notes=f"Notas del contrato #{i+1}: Observaciones importantes para el seguimiento.",
                contract_file=f"contratos/contrato_{i+1:03d}.pdf",
                created_by=user
            )
            contracts.append(contract)
        
        return contracts


class ContractPayment(models.Model):
    """Modelo para pagos asociados a contratos"""
    
    PAYMENT_TYPES = [
        ('initial', 'Pago Inicial'),
        ('monthly', 'Cuota Mensual'),
        ('commission', 'Comisión'),
        ('penalty', 'Multa'),
        ('deposit', 'Depósito'),
        ('final', 'Pago Final'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('overdue', 'Vencido'),
        ('partial', 'Parcial'),
        ('cancelled', 'Cancelado'),
    ]
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='payments', verbose_name='Contrato')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES, verbose_name='Tipo de Pago')
    amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Monto')
    due_date = models.DateField(verbose_name='Fecha de Vencimiento')
    paid_date = models.DateField(blank=True, null=True, verbose_name='Fecha de Pago')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Estado')
    
    # Detalles del pago
    payment_method = models.CharField(max_length=50, blank=True, verbose_name='Método de Pago')
    reference_number = models.CharField(max_length=100, blank=True, verbose_name='Número de Referencia')
    notes = models.TextField(blank=True, verbose_name='Notas')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Pago de Contrato'
        verbose_name_plural = 'Pagos de Contratos'
        ordering = ['due_date']
    
    def __str__(self):
        return f"{self.contract.contract_number} - {self.get_payment_type_display()} - ${self.amount:,.0f}"
    
    def is_overdue(self):
        """Verifica si el pago está vencido"""
        return self.status == 'pending' and self.due_date < timezone.now().date()
    
    def days_overdue(self):
        """Calcula los días de retraso"""
        if self.is_overdue():
            return (timezone.now().date() - self.due_date).days
        return 0


class ContractDocument(models.Model):
    """Modelo para documentos asociados a contratos"""
    
    DOCUMENT_TYPES = [
        ('contract', 'Contrato Principal'),
        ('addendum', 'Adenda'),
        ('certificate', 'Certificado'),
        ('invoice', 'Factura'),
        ('receipt', 'Recibo'),
        ('legal', 'Documento Legal'),
        ('technical', 'Documento Técnico'),
        ('other', 'Otro'),
    ]
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='documents', verbose_name='Contrato')
    name = models.CharField(max_length=200, verbose_name='Nombre del Documento')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES, verbose_name='Tipo de Documento')
    file_path = models.CharField(max_length=255, verbose_name='Ruta del Archivo')
    file_size = models.CharField(max_length=20, blank=True, verbose_name='Tamaño del Archivo')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Subido por')
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Subida')
    
    class Meta:
        verbose_name = 'Documento de Contrato'
        verbose_name_plural = 'Documentos de Contratos'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.contract.contract_number} - {self.name}"


class ContractNote(models.Model):
    """Modelo para notas y comentarios de contratos"""
    
    NOTE_TYPES = [
        ('general', 'General'),
        ('important', 'Importante'),
        ('reminder', 'Recordatorio'),
        ('issue', 'Problema'),
        ('update', 'Actualización'),
    ]
    
    contract = models.ForeignKey(Contract, on_delete=models.CASCADE, related_name='contract_notes', verbose_name='Contrato')
    note_type = models.CharField(max_length=20, choices=NOTE_TYPES, default='general', verbose_name='Tipo de Nota')
    title = models.CharField(max_length=200, verbose_name='Título')
    content = models.TextField(verbose_name='Contenido')
    is_important = models.BooleanField(default=False, verbose_name='Es Importante')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
    class Meta:
        verbose_name = 'Nota de Contrato'
        verbose_name_plural = 'Notas de Contratos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.contract.contract_number} - {self.title}"

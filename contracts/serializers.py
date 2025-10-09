from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Contract, ContractPayment, ContractDocument, ContractNote

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para información de usuario"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ContractPaymentSerializer(serializers.ModelSerializer):
    """Serializer para pagos de contratos"""
    
    payment_type_display = serializers.CharField(source='get_payment_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = ContractPayment
        fields = [
            'id', 'payment_type', 'payment_type_display', 'amount', 'due_date',
            'paid_date', 'status', 'status_display', 'payment_method',
            'reference_number', 'notes', 'is_overdue', 'days_overdue',
            'created_at', 'updated_at'
        ]


class ContractDocumentSerializer(serializers.ModelSerializer):
    """Serializer para documentos de contratos"""
    
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    uploaded_by_info = UserBasicSerializer(source='uploaded_by', read_only=True)
    
    class Meta:
        model = ContractDocument
        fields = [
            'id', 'name', 'document_type', 'document_type_display',
            'file_path', 'file_size', 'description', 'uploaded_by',
            'uploaded_by_info', 'uploaded_at'
        ]


class ContractNoteSerializer(serializers.ModelSerializer):
    """Serializer para notas de contratos"""
    
    note_type_display = serializers.CharField(source='get_note_type_display', read_only=True)
    created_by_info = UserBasicSerializer(source='created_by', read_only=True)
    
    class Meta:
        model = ContractNote
        fields = [
            'id', 'note_type', 'note_type_display', 'title', 'content',
            'is_important', 'created_by', 'created_by_info', 'created_at'
        ]


class ContractListSerializer(serializers.ModelSerializer):
    """Serializer para listado de contratos (vista resumida)"""
    
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    agent_info = UserBasicSerializer(source='agent', read_only=True)
    created_by_info = UserBasicSerializer(source='created_by', read_only=True)
    
    # Campos calculados
    status_color = serializers.CharField(read_only=True)
    priority_color = serializers.CharField(read_only=True)
    type_icon = serializers.CharField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'title', 'contract_type', 'contract_type_display',
            'status', 'status_display', 'status_color', 'priority', 'priority_display',
            'priority_color', 'type_icon', 'client_name', 'agent', 'agent_info',
            'property_address', 'property_type', 'contract_value', 'commission_amount',
            'start_date', 'end_date', 'signed_date', 'is_expired', 'days_until_expiry',
            'progress_percentage', 'created_by', 'created_by_info', 'created_at', 'updated_at'
        ]


class ContractDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles de contratos"""
    
    contract_type_display = serializers.CharField(source='get_contract_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    agent_info = UserBasicSerializer(source='agent', read_only=True)
    created_by_info = UserBasicSerializer(source='created_by', read_only=True)
    
    # Relaciones anidadas
    payments = ContractPaymentSerializer(many=True, read_only=True)
    documents = ContractDocumentSerializer(many=True, read_only=True)
    notes = ContractNoteSerializer(many=True, read_only=True)
    
    # Campos calculados
    status_color = serializers.CharField(read_only=True)
    priority_color = serializers.CharField(read_only=True)
    type_icon = serializers.CharField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    duration_days = serializers.IntegerField(source='get_duration_days', read_only=True)
    progress_percentage = serializers.FloatField(read_only=True)
    
    # Estadísticas
    total_payments = serializers.SerializerMethodField()
    pending_payments = serializers.SerializerMethodField()
    overdue_payments = serializers.SerializerMethodField()
    documents_count = serializers.SerializerMethodField()
    notes_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Contract
        fields = [
            'id', 'contract_number', 'title', 'contract_type', 'contract_type_display',
            'status', 'status_display', 'status_color', 'priority', 'priority_display',
            'priority_color', 'type_icon', 'client_name', 'client_email', 'client_phone',
            'client_address', 'agent', 'agent_info', 'property_address', 'property_type',
            'contract_value', 'commission_rate', 'commission_amount', 'start_date',
            'end_date', 'signed_date', 'terms_and_conditions', 'special_clauses',
            'notes', 'contract_file', 'attachments', 'is_expired', 'days_until_expiry',
            'duration_days', 'progress_percentage', 'created_by', 'created_by_info',
            'created_at', 'updated_at', 'payments', 'documents', 'notes',
            'total_payments', 'pending_payments', 'overdue_payments',
            'documents_count', 'notes_count'
        ]
    
    def get_total_payments(self, obj):
        """Retorna el número total de pagos"""
        return obj.payments.count()
    
    def get_pending_payments(self, obj):
        """Retorna el número de pagos pendientes"""
        return obj.payments.filter(status='pending').count()
    
    def get_overdue_payments(self, obj):
        """Retorna el número de pagos vencidos"""
        return obj.payments.filter(status='pending', due_date__lt=timezone.now().date()).count()
    
    def get_documents_count(self, obj):
        """Retorna el número de documentos"""
        return obj.documents.count()
    
    def get_notes_count(self, obj):
        """Retorna el número de notas"""
        return obj.notes.count()


class ContractCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar contratos"""
    
    class Meta:
        model = Contract
        fields = [
            'title', 'contract_type', 'status', 'priority', 'client_name',
            'client_email', 'client_phone', 'client_address', 'agent',
            'property_address', 'property_type', 'contract_value',
            'commission_rate', 'start_date', 'end_date', 'signed_date',
            'terms_and_conditions', 'special_clauses', 'notes',
            'contract_file', 'attachments'
        ]
    
    def validate_contract_value(self, value):
        """Valida que el valor del contrato sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El valor del contrato debe ser mayor a cero.")
        return value
    
    def validate_commission_rate(self, value):
        """Valida que la tasa de comisión esté en un rango válido"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("La tasa de comisión debe estar entre 0% y 100%.")
        return value
    
    def validate(self, data):
        """Validaciones a nivel de objeto"""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and end_date <= start_date:
            raise serializers.ValidationError({
                'end_date': 'La fecha de finalización debe ser posterior a la fecha de inicio.'
            })
        
        signed_date = data.get('signed_date')
        if signed_date and start_date and signed_date > start_date:
            raise serializers.ValidationError({
                'signed_date': 'La fecha de firma no puede ser posterior a la fecha de inicio.'
            })
        
        return data
    
    def create(self, validated_data):
        """Crea un nuevo contrato"""
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class ContractStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de contratos"""
    
    total_contracts = serializers.IntegerField()
    active_contracts = serializers.IntegerField()
    pending_contracts = serializers.IntegerField()
    signed_contracts = serializers.IntegerField()
    completed_contracts = serializers.IntegerField()
    cancelled_contracts = serializers.IntegerField()
    expired_contracts = serializers.IntegerField()
    
    # Por tipo
    sale_contracts = serializers.IntegerField()
    rent_contracts = serializers.IntegerField()
    lease_contracts = serializers.IntegerField()
    management_contracts = serializers.IntegerField()
    
    # Por prioridad
    high_priority_contracts = serializers.IntegerField()
    urgent_priority_contracts = serializers.IntegerField()
    
    # Valores monetarios
    total_contract_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_commission_amount = serializers.DecimalField(max_digits=20, decimal_places=2)
    
    # Fechas
    contracts_this_month = serializers.IntegerField()
    contracts_this_year = serializers.IntegerField()
    
    # Próximos vencimientos
    expiring_soon = serializers.IntegerField()  # Próximos 30 días
    
    # Pagos
    total_payments = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    overdue_payments = serializers.IntegerField()


class ContractSummarySerializer(serializers.Serializer):
    """Serializer para resumen de contratos por agente"""
    
    agent_id = serializers.IntegerField()
    agent_name = serializers.CharField()
    total_contracts = serializers.IntegerField()
    active_contracts = serializers.IntegerField()
    total_value = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_commission = serializers.DecimalField(max_digits=20, decimal_places=2)


class ContractBulkActionSerializer(serializers.Serializer):
    """Serializer para acciones en lote sobre contratos"""
    
    ACTION_CHOICES = [
        ('activate', 'Activar'),
        ('deactivate', 'Desactivar'),
        ('sign', 'Marcar como Firmado'),
        ('complete', 'Completar'),
        ('cancel', 'Cancelar'),
        ('delete', 'Eliminar'),
    ]
    
    contract_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=100
    )
    action = serializers.ChoiceField(choices=ACTION_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
    
    def validate_contract_ids(self, value):
        """Valida que los IDs de contratos existan"""
        existing_ids = Contract.objects.filter(id__in=value).values_list('id', flat=True)
        missing_ids = set(value) - set(existing_ids)
        
        if missing_ids:
            raise serializers.ValidationError(
                f"Los siguientes contratos no existen: {list(missing_ids)}"
            )
        
        return value
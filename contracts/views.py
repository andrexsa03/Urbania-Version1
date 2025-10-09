from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from .models import Contract, ContractPayment, ContractDocument, ContractNote
from .serializers import (
    ContractListSerializer, ContractDetailSerializer, ContractCreateUpdateSerializer,
    ContractPaymentSerializer, ContractDocumentSerializer, ContractNoteSerializer,
    ContractStatsSerializer, ContractSummarySerializer, ContractBulkActionSerializer
)


class ContractListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear contratos"""
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'contract_type', 'priority', 'agent']
    search_fields = ['title', 'contract_number', 'client_name', 'property_address']
    ordering_fields = ['created_at', 'start_date', 'end_date', 'contract_value', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Retorna contratos del usuario actual o todos si es admin"""
        queryset = Contract.objects.select_related('agent', 'created_by')
        
        # Filtrar por agente si no es admin
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(agent=self.request.user) | Q(created_by=self.request.user)
            )
        
        # Filtros adicionales
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        contract_type_filter = self.request.query_params.get('contract_type')
        if contract_type_filter:
            queryset = queryset.filter(contract_type=contract_type_filter)
        
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Filtro por fechas
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        # Filtro por valor del contrato
        min_value = self.request.query_params.get('min_value')
        max_value = self.request.query_params.get('max_value')
        
        if min_value:
            queryset = queryset.filter(contract_value__gte=min_value)
        if max_value:
            queryset = queryset.filter(contract_value__lte=max_value)
        
        return queryset
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.request.method == 'POST':
            return ContractCreateUpdateSerializer
        return ContractListSerializer


class ContractDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar un contrato específico"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retorna contratos del usuario actual o todos si es admin"""
        queryset = Contract.objects.select_related('agent', 'created_by').prefetch_related(
            'payments', 'documents', 'notes'
        )
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                Q(agent=self.request.user) | Q(created_by=self.request.user)
            )
        
        return queryset
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.request.method in ['PUT', 'PATCH']:
            return ContractCreateUpdateSerializer
        return ContractDetailSerializer


class ContractPaymentListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear pagos de contratos"""
    
    serializer_class = ContractPaymentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_type']
    ordering_fields = ['due_date', 'amount', 'created_at']
    ordering = ['due_date']
    
    def get_queryset(self):
        """Retorna pagos del contrato especificado"""
        contract_id = self.kwargs.get('contract_id')
        return ContractPayment.objects.filter(contract_id=contract_id)
    
    def perform_create(self, serializer):
        """Asocia el pago al contrato especificado"""
        contract_id = self.kwargs.get('contract_id')
        contract = Contract.objects.get(id=contract_id)
        serializer.save(contract=contract)


class ContractDocumentListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear documentos de contratos"""
    
    serializer_class = ContractDocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['document_type']
    ordering_fields = ['uploaded_at', 'name']
    ordering = ['-uploaded_at']
    
    def get_queryset(self):
        """Retorna documentos del contrato especificado"""
        contract_id = self.kwargs.get('contract_id')
        return ContractDocument.objects.filter(contract_id=contract_id)
    
    def perform_create(self, serializer):
        """Asocia el documento al contrato especificado"""
        contract_id = self.kwargs.get('contract_id')
        contract = Contract.objects.get(id=contract_id)
        serializer.save(contract=contract, uploaded_by=self.request.user)


class ContractNoteListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear notas de contratos"""
    
    serializer_class = ContractNoteSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['note_type', 'is_important']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Retorna notas del contrato especificado"""
        contract_id = self.kwargs.get('contract_id')
        return ContractNote.objects.filter(contract_id=contract_id)
    
    def perform_create(self, serializer):
        """Asocia la nota al contrato especificado"""
        contract_id = self.kwargs.get('contract_id')
        contract = Contract.objects.get(id=contract_id)
        serializer.save(contract=contract, created_by=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contract_stats(request):
    """Estadísticas generales de contratos"""
    
    # Filtrar contratos según permisos del usuario
    if request.user.is_staff:
        contracts = Contract.objects.all()
    else:
        contracts = Contract.objects.filter(
            Q(agent=request.user) | Q(created_by=request.user)
        )
    
    # Estadísticas básicas
    total_contracts = contracts.count()
    active_contracts = contracts.filter(status='active').count()
    pending_contracts = contracts.filter(status='pending').count()
    signed_contracts = contracts.filter(status='signed').count()
    completed_contracts = contracts.filter(status='completed').count()
    cancelled_contracts = contracts.filter(status='cancelled').count()
    expired_contracts = contracts.filter(status='expired').count()
    
    # Por tipo de contrato
    sale_contracts = contracts.filter(contract_type='sale').count()
    rent_contracts = contracts.filter(contract_type='rent').count()
    lease_contracts = contracts.filter(contract_type='lease').count()
    management_contracts = contracts.filter(contract_type='management').count()
    
    # Por prioridad
    high_priority_contracts = contracts.filter(priority='high').count()
    urgent_priority_contracts = contracts.filter(priority='urgent').count()
    
    # Valores monetarios
    total_contract_value = contracts.aggregate(
        total=Sum('contract_value')
    )['total'] or Decimal('0')
    
    total_commission_amount = contracts.aggregate(
        total=Sum('commission_amount')
    )['total'] or Decimal('0')
    
    # Contratos por período
    today = timezone.now().date()
    first_day_month = today.replace(day=1)
    first_day_year = today.replace(month=1, day=1)
    
    contracts_this_month = contracts.filter(created_at__date__gte=first_day_month).count()
    contracts_this_year = contracts.filter(created_at__date__gte=first_day_year).count()
    
    # Contratos que vencen pronto (próximos 30 días)
    thirty_days_from_now = today + timedelta(days=30)
    expiring_soon = contracts.filter(
        end_date__lte=thirty_days_from_now,
        end_date__gte=today,
        status__in=['active', 'signed']
    ).count()
    
    # Estadísticas de pagos
    all_payments = ContractPayment.objects.filter(contract__in=contracts)
    total_payments = all_payments.count()
    pending_payments = all_payments.filter(status='pending').count()
    overdue_payments = all_payments.filter(
        status='pending',
        due_date__lt=today
    ).count()
    
    stats_data = {
        'total_contracts': total_contracts,
        'active_contracts': active_contracts,
        'pending_contracts': pending_contracts,
        'signed_contracts': signed_contracts,
        'completed_contracts': completed_contracts,
        'cancelled_contracts': cancelled_contracts,
        'expired_contracts': expired_contracts,
        'sale_contracts': sale_contracts,
        'rent_contracts': rent_contracts,
        'lease_contracts': lease_contracts,
        'management_contracts': management_contracts,
        'high_priority_contracts': high_priority_contracts,
        'urgent_priority_contracts': urgent_priority_contracts,
        'total_contract_value': total_contract_value,
        'total_commission_amount': total_commission_amount,
        'contracts_this_month': contracts_this_month,
        'contracts_this_year': contracts_this_year,
        'expiring_soon': expiring_soon,
        'total_payments': total_payments,
        'pending_payments': pending_payments,
        'overdue_payments': overdue_payments,
    }
    
    serializer = ContractStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_contract_status(request, pk):
    """Actualiza el estado de un contrato"""
    
    try:
        contract = Contract.objects.get(pk=pk)
        
        # Verificar permisos
        if not request.user.is_staff and contract.agent != request.user and contract.created_by != request.user:
            return Response(
                {'error': 'No tienes permisos para modificar este contrato'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        new_status = request.data.get('status')
        if not new_status:
            return Response(
                {'error': 'El campo status es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validar que el estado sea válido
        valid_statuses = [choice[0] for choice in Contract.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return Response(
                {'error': f'Estado inválido. Estados válidos: {valid_statuses}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        contract.status = new_status
        
        # Si se marca como firmado, establecer fecha de firma
        if new_status == 'signed' and not contract.signed_date:
            contract.signed_date = timezone.now().date()
        
        contract.save()
        
        serializer = ContractDetailSerializer(contract)
        return Response(serializer.data)
        
    except Contract.DoesNotExist:
        return Response(
            {'error': 'Contrato no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def bulk_contract_actions(request):
    """Acciones en lote sobre contratos"""
    
    serializer = ContractBulkActionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    contract_ids = serializer.validated_data['contract_ids']
    action = serializer.validated_data['action']
    notes = serializer.validated_data.get('notes', '')
    
    # Filtrar contratos según permisos del usuario
    contracts = Contract.objects.filter(id__in=contract_ids)
    if not request.user.is_staff:
        contracts = contracts.filter(
            Q(agent=request.user) | Q(created_by=request.user)
        )
    
    if not contracts.exists():
        return Response(
            {'error': 'No se encontraron contratos válidos para procesar'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    updated_count = 0
    
    # Ejecutar acción según el tipo
    if action == 'activate':
        updated_count = contracts.update(status='active')
    elif action == 'deactivate':
        updated_count = contracts.update(status='draft')
    elif action == 'sign':
        updated_count = contracts.update(
            status='signed',
            signed_date=timezone.now().date()
        )
    elif action == 'complete':
        updated_count = contracts.update(status='completed')
    elif action == 'cancel':
        updated_count = contracts.update(status='cancelled')
    elif action == 'delete':
        updated_count = contracts.count()
        contracts.delete()
    
    return Response({
        'message': f'Acción {action} ejecutada exitosamente',
        'updated_count': updated_count,
        'notes': notes
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_contracts(request):
    """Búsqueda avanzada de contratos"""
    
    query = request.GET.get('q', '')
    if not query:
        return Response({'results': []})
    
    # Filtrar contratos según permisos del usuario
    contracts = Contract.objects.select_related('agent', 'created_by')
    if not request.user.is_staff:
        contracts = contracts.filter(
            Q(agent=request.user) | Q(created_by=request.user)
        )
    
    # Búsqueda en múltiples campos
    contracts = contracts.filter(
        Q(title__icontains=query) |
        Q(contract_number__icontains=query) |
        Q(client_name__icontains=query) |
        Q(property_address__icontains=query) |
        Q(property_type__icontains=query) |
        Q(notes__icontains=query)
    ).distinct()[:20]  # Limitar a 20 resultados
    
    serializer = ContractListSerializer(contracts, many=True)
    return Response({'results': serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_contracts(request):
    """Contratos del usuario actual"""
    
    contracts = Contract.objects.filter(
        Q(agent=request.user) | Q(created_by=request.user)
    ).select_related('agent', 'created_by')
    
    # Filtros opcionales
    status_filter = request.GET.get('status')
    if status_filter:
        contracts = contracts.filter(status=status_filter)
    
    serializer = ContractListSerializer(contracts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expiring_contracts(request):
    """Contratos que vencen pronto"""
    
    days = int(request.GET.get('days', 30))  # Por defecto 30 días
    end_date = timezone.now().date() + timedelta(days=days)
    
    # Filtrar contratos según permisos del usuario
    contracts = Contract.objects.select_related('agent', 'created_by')
    if not request.user.is_staff:
        contracts = contracts.filter(
            Q(agent=request.user) | Q(created_by=request.user)
        )
    
    contracts = contracts.filter(
        end_date__lte=end_date,
        end_date__gte=timezone.now().date(),
        status__in=['active', 'signed']
    ).order_by('end_date')
    
    serializer = ContractListSerializer(contracts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def contract_summary_by_agent(request):
    """Resumen de contratos por agente"""
    
    if not request.user.is_staff:
        return Response(
            {'error': 'No tienes permisos para ver esta información'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Agrupar contratos por agente
    summary = Contract.objects.values(
        'agent__id', 'agent__first_name', 'agent__last_name'
    ).annotate(
        total_contracts=Count('id'),
        active_contracts=Count('id', filter=Q(status='active')),
        total_value=Sum('contract_value'),
        total_commission=Sum('commission_amount')
    ).order_by('-total_contracts')
    
    # Formatear datos para el serializer
    summary_data = []
    for item in summary:
        agent_name = f"{item['agent__first_name']} {item['agent__last_name']}".strip()
        if not agent_name:
            agent_name = f"Usuario {item['agent__id']}"
        
        summary_data.append({
            'agent_id': item['agent__id'],
            'agent_name': agent_name,
            'total_contracts': item['total_contracts'],
            'active_contracts': item['active_contracts'],
            'total_value': item['total_value'] or Decimal('0'),
            'total_commission': item['total_commission'] or Decimal('0')
        })
    
    serializer = ContractSummarySerializer(summary_data, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_mock_contracts(request):
    """Genera contratos mock para pruebas"""
    
    count = int(request.data.get('count', 10))
    if count > 50:
        count = 50  # Limitar a 50 contratos por solicitud
    
    contracts = Contract.generate_mock_contracts(request.user, count)
    
    return Response({
        'message': f'{len(contracts)} contratos mock generados exitosamente',
        'contracts_created': len(contracts)
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_user_contracts(request):
    """Elimina todos los contratos del usuario actual"""
    
    contracts = Contract.objects.filter(
        Q(agent=request.user) | Q(created_by=request.user)
    )
    
    count = contracts.count()
    contracts.delete()
    
    return Response({
        'message': f'{count} contratos eliminados exitosamente',
        'deleted_count': count
    })

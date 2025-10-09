from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
import random

from .models import Report, ReportChart, ReportData, ReportSubscription
from .serializers import (
    ReportSerializer, ReportCreateSerializer, ReportUpdateSerializer,
    ReportListSerializer, ReportStatsSerializer, ReportChartSerializer,
    ReportSubscriptionSerializer, ReportSubscriptionCreateSerializer,
    ReportGenerateSerializer, ReportExportSerializer, ReportSearchSerializer
)


class ReportListCreateView(generics.ListCreateAPIView):
    """Vista para listar y crear reportes"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'status', 'period', 'is_public', 'created_by']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'updated_at', 'name', 'total_records']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filtra reportes según permisos del usuario"""
        queryset = Report.objects.select_related('created_by').prefetch_related('charts')
        
        # Filtros adicionales
        if self.request.query_params.get('my_reports'):
            queryset = queryset.filter(created_by=self.request.user)
        
        if self.request.query_params.get('public_only'):
            queryset = queryset.filter(is_public=True)
        
        if self.request.query_params.get('expired'):
            queryset = queryset.filter(expires_at__lt=timezone.now())
        
        # Filtro por rango de fechas
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        return queryset
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.request.method == 'POST':
            return ReportCreateSerializer
        return ReportListSerializer


class ReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para obtener, actualizar y eliminar reportes individuales"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Report.objects.select_related('created_by').prefetch_related(
            'charts__data'
        )
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.request.method in ['PUT', 'PATCH']:
            return ReportUpdateSerializer
        return ReportSerializer


class ReportChartListView(generics.ListCreateAPIView):
    """Vista para listar y crear gráficos de un reporte"""
    serializer_class = ReportChartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        report_id = self.kwargs['report_id']
        return ReportChart.objects.filter(
            report_id=report_id,
            is_active=True
        ).prefetch_related('data').order_by('order')
    
    def perform_create(self, serializer):
        """Asocia el gráfico al reporte"""
        report_id = self.kwargs['report_id']
        serializer.save(report_id=report_id)


class ReportSubscriptionListView(generics.ListCreateAPIView):
    """Vista para listar y crear suscripciones a reportes"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ReportSubscription.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ReportSubscriptionCreateSerializer
        return ReportSubscriptionSerializer


class ReportSubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vista para gestionar suscripciones individuales"""
    serializer_class = ReportSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ReportSubscription.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def report_stats(request):
    """Estadísticas generales de reportes"""
    # Estadísticas básicas
    total_reports = Report.objects.count()
    user_reports = Report.objects.filter(created_by=request.user).count()
    
    # Reportes por tipo
    reports_by_type = dict(
        Report.objects.values('report_type').annotate(
            count=Count('id')
        ).values_list('report_type', 'count')
    )
    
    # Reportes por estado
    reports_by_status = dict(
        Report.objects.values('status').annotate(
            count=Count('id')
        ).values_list('status', 'count')
    )
    
    # Reportes por período
    reports_by_period = dict(
        Report.objects.values('period').annotate(
            count=Count('id')
        ).values_list('period', 'count')
    )
    
    # Reportes recientes
    recent_reports = Report.objects.select_related('created_by').order_by('-created_at')[:5]
    
    # Tipos más populares
    popular_types = list(
        Report.objects.values('report_type').annotate(
            count=Count('id')
        ).order_by('-count')[:3].values_list('report_type', flat=True)
    )
    
    # Promedio de registros por reporte
    avg_records = Report.objects.aggregate(
        avg=Avg('total_records')
    )['avg'] or 0
    
    stats_data = {
        'total_reports': total_reports,
        'user_reports': user_reports,
        'reports_by_type': reports_by_type,
        'reports_by_status': reports_by_status,
        'reports_by_period': reports_by_period,
        'recent_reports': recent_reports,
        'popular_types': popular_types,
        'avg_records_per_report': round(avg_records, 2)
    }
    
    serializer = ReportStatsSerializer(stats_data)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_report(request):
    """Genera un reporte con datos mock"""
    serializer = ReportGenerateSerializer(data=request.data)
    
    if serializer.is_valid():
        data = serializer.validated_data
        
        # Crear el reporte
        report = Report.objects.create(
            name=f"Reporte {data['report_type'].title()} - {data['period'].title()}",
            report_type=data['report_type'],
            period=data['period'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            description=f"Reporte generado automáticamente para {data['report_type']}",
            total_records=random.randint(100, 1000),
            file_size=f"{random.randint(1, 20)} MB",
            created_by=request.user,
            status='ready'
        )
        
        # Generar gráficos mock si se solicita
        if data.get('include_charts', True):
            chart_types = data.get('chart_types', ['bar', 'line', 'pie'])
            
            for i, chart_type in enumerate(chart_types[:3]):  # Máximo 3 gráficos
                chart = ReportChart.objects.create(
                    report=report,
                    title=f"Gráfico {chart_type.title()} - {report.get_report_type_display()}",
                    chart_type=chart_type,
                    description=f"Análisis de {report.get_report_type_display().lower()}",
                    x_axis_label="Período",
                    y_axis_label="Valor",
                    order=i
                )
                
                # Generar datos mock para el gráfico
                _generate_mock_chart_data(chart)
        
        return Response(
            ReportSerializer(report).data,
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def export_report(request, pk):
    """Exporta un reporte en diferentes formatos"""
    try:
        report = Report.objects.get(pk=pk)
    except Report.DoesNotExist:
        return Response(
            {'error': 'Reporte no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = ReportExportSerializer(data=request.data)
    
    if serializer.is_valid():
        export_format = serializer.validated_data['format']
        
        # Simulación de exportación
        export_data = {
            'message': f'Reporte exportado exitosamente en formato {export_format.upper()}',
            'report_id': report.id,
            'report_name': report.name,
            'format': export_format,
            'file_size': f"{random.randint(1, 10)} MB",
            'download_url': f'/api/reportes/{pk}/download/{export_format}/',
            'expires_at': (timezone.now() + timedelta(hours=24)).isoformat()
        }
        
        return Response(export_data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_reports(request):
    """Búsqueda avanzada de reportes"""
    serializer = ReportSearchSerializer(data=request.query_params)
    
    if serializer.is_valid():
        data = serializer.validated_data
        queryset = Report.objects.select_related('created_by')
        
        # Filtro por texto
        if 'query' in data:
            queryset = queryset.filter(
                Q(name__icontains=data['query']) |
                Q(description__icontains=data['query'])
            )
        
        # Filtros adicionales
        for field in ['report_type', 'status', 'period', 'is_public']:
            if field in data:
                queryset = queryset.filter(**{field: data[field]})
        
        # Filtros de fecha
        if 'start_date' in data:
            queryset = queryset.filter(start_date__gte=data['start_date'])
        if 'end_date' in data:
            queryset = queryset.filter(end_date__lte=data['end_date'])
        
        # Filtro por creador
        if 'created_by' in data:
            queryset = queryset.filter(created_by_id=data['created_by'])
        
        reports = queryset.order_by('-created_at')[:20]  # Limitar resultados
        
        return Response(ReportListSerializer(reports, many=True).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_reports(request):
    """Reportes del usuario actual"""
    reports = Report.objects.filter(
        created_by=request.user
    ).select_related('created_by').order_by('-created_at')
    
    return Response(ReportListSerializer(reports, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def public_reports(request):
    """Reportes públicos"""
    reports = Report.objects.filter(
        is_public=True
    ).select_related('created_by').order_by('-created_at')
    
    return Response(ReportListSerializer(reports, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_mock_data(request):
    """Genera datos mock para pruebas"""
    count = int(request.data.get('count', 10))
    
    # Generar reportes mock
    reports = Report.generate_mock_reports(request.user, count)
    
    # Generar gráficos y datos para algunos reportes
    for report in reports[:5]:  # Solo para los primeros 5
        for i in range(random.randint(1, 3)):
            chart = ReportChart.objects.create(
                report=report,
                title=f"Gráfico {i+1} - {report.name}",
                chart_type=random.choice(['bar', 'line', 'pie', 'doughnut']),
                description=f"Análisis de {report.get_report_type_display().lower()}",
                x_axis_label="Período",
                y_axis_label="Valor",
                order=i
            )
            _generate_mock_chart_data(chart)
    
    return Response({
        'message': f'{count} reportes mock generados exitosamente',
        'reports_created': len(reports)
    })


def _generate_mock_chart_data(chart):
    """Función auxiliar para generar datos mock de gráficos"""
    if chart.chart_type in ['pie', 'doughnut']:
        # Datos para gráficos circulares
        labels = ['Casas', 'Apartamentos', 'Oficinas', 'Locales', 'Terrenos']
        colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
        
        for i, label in enumerate(labels):
            ReportData.objects.create(
                chart=chart,
                label=label,
                value=random.randint(10, 40),
                color=colors[i],
                order=i
            )
    
    else:
        # Datos para gráficos de líneas/barras
        months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
        
        for i, month in enumerate(months):
            ReportData.objects.create(
                chart=chart,
                label=month,
                value=random.randint(1000, 50000),
                color='#36A2EB',
                order=i
            )

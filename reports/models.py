from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()


class Report(models.Model):
    """Modelo para reportes gerenciales"""
    
    REPORT_TYPES = [
        ('sales', 'Reporte de Ventas'),
        ('properties', 'Reporte de Propiedades'),
        ('clients', 'Reporte de Clientes'),
        ('agents', 'Reporte de Agentes'),
        ('financial', 'Reporte Financiero'),
        ('marketing', 'Reporte de Marketing'),
        ('performance', 'Reporte de Rendimiento'),
    ]
    
    PERIODS = [
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
        ('custom', 'Personalizado'),
    ]
    
    STATUS_CHOICES = [
        ('generating', 'Generando'),
        ('ready', 'Listo'),
        ('error', 'Error'),
        ('expired', 'Expirado'),
    ]
    
    name = models.CharField(max_length=200, verbose_name='Nombre del Reporte')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name='Tipo de Reporte')
    period = models.CharField(max_length=20, choices=PERIODS, verbose_name='Período')
    start_date = models.DateField(verbose_name='Fecha Inicio')
    end_date = models.DateField(verbose_name='Fecha Fin')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ready', verbose_name='Estado')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    # Metadatos del reporte
    total_records = models.IntegerField(default=0, verbose_name='Total de Registros')
    file_size = models.CharField(max_length=50, blank=True, verbose_name='Tamaño del Archivo')
    
    # Usuario y fechas
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Creado por')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Expiración')
    
    # Configuración
    is_public = models.BooleanField(default=False, verbose_name='Público')
    auto_refresh = models.BooleanField(default=False, verbose_name='Actualización Automática')
    
    class Meta:
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()}"
    
    def is_expired(self):
        """Verifica si el reporte ha expirado"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def get_status_color(self):
        """Retorna el color del estado"""
        colors = {
            'generating': 'warning',
            'ready': 'success',
            'error': 'danger',
            'expired': 'secondary'
        }
        return colors.get(self.status, 'secondary')
    
    def get_period_display_extended(self):
        """Retorna el período con fechas"""
        period_display = self.get_period_display()
        return f"{period_display} ({self.start_date} - {self.end_date})"
    
    @classmethod
    def generate_mock_reports(cls, user, count=10):
        """Genera reportes mock para pruebas"""
        reports = []
        report_names = [
            'Ventas Mensuales Enero 2024',
            'Propiedades Activas Q1',
            'Rendimiento de Agentes',
            'Análisis de Clientes Premium',
            'Reporte Financiero Trimestral',
            'Marketing Digital ROI',
            'Comisiones por Zona',
            'Propiedades Vendidas',
            'Leads Generados',
            'Satisfacción del Cliente'
        ]
        
        for i in range(count):
            start_date = timezone.now().date() - timedelta(days=random.randint(1, 90))
            end_date = start_date + timedelta(days=random.randint(7, 30))
            
            report = cls.objects.create(
                name=random.choice(report_names),
                report_type=random.choice([choice[0] for choice in cls.REPORT_TYPES]),
                period=random.choice([choice[0] for choice in cls.PERIODS]),
                start_date=start_date,
                end_date=end_date,
                status=random.choice([choice[0] for choice in cls.STATUS_CHOICES]),
                description=f"Reporte generado automáticamente para análisis de {random.choice(['ventas', 'propiedades', 'clientes', 'agentes'])}",
                total_records=random.randint(50, 1000),
                file_size=f"{random.randint(1, 50)} MB",
                created_by=user,
                is_public=random.choice([True, False]),
                auto_refresh=random.choice([True, False])
            )
            reports.append(report)
        
        return reports


class ReportChart(models.Model):
    """Modelo para gráficos de reportes"""
    
    CHART_TYPES = [
        ('line', 'Líneas'),
        ('bar', 'Barras'),
        ('pie', 'Circular'),
        ('doughnut', 'Dona'),
        ('area', 'Área'),
        ('scatter', 'Dispersión'),
        ('radar', 'Radar'),
    ]
    
    report = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='charts', verbose_name='Reporte')
    title = models.CharField(max_length=200, verbose_name='Título del Gráfico')
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, verbose_name='Tipo de Gráfico')
    description = models.TextField(blank=True, verbose_name='Descripción')
    
    # Configuración del gráfico
    x_axis_label = models.CharField(max_length=100, blank=True, verbose_name='Etiqueta Eje X')
    y_axis_label = models.CharField(max_length=100, blank=True, verbose_name='Etiqueta Eje Y')
    show_legend = models.BooleanField(default=True, verbose_name='Mostrar Leyenda')
    show_grid = models.BooleanField(default=True, verbose_name='Mostrar Grilla')
    
    # Orden y estado
    order = models.IntegerField(default=0, verbose_name='Orden')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
    class Meta:
        verbose_name = 'Gráfico de Reporte'
        verbose_name_plural = 'Gráficos de Reportes'
        ordering = ['report', 'order']
    
    def __str__(self):
        return f"{self.report.name} - {self.title}"


class ReportData(models.Model):
    """Modelo para datos de gráficos de reportes"""
    
    chart = models.ForeignKey(ReportChart, on_delete=models.CASCADE, related_name='data', verbose_name='Gráfico')
    label = models.CharField(max_length=100, verbose_name='Etiqueta')
    value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name='Valor')
    color = models.CharField(max_length=7, blank=True, verbose_name='Color')
    
    # Datos adicionales para series múltiples
    series_name = models.CharField(max_length=100, blank=True, verbose_name='Nombre de Serie')
    date = models.DateField(null=True, blank=True, verbose_name='Fecha')
    
    # Orden
    order = models.IntegerField(default=0, verbose_name='Orden')
    
    class Meta:
        verbose_name = 'Dato de Gráfico'
        verbose_name_plural = 'Datos de Gráficos'
        ordering = ['chart', 'order', 'date']
    
    def __str__(self):
        return f"{self.chart.title} - {self.label}: {self.value}"
    
    def get_formatted_value(self):
        """Retorna el valor formateado según el tipo de gráfico"""
        if self.chart.chart_type in ['pie', 'doughnut']:
            return f"{self.value}%"
        elif 'ventas' in self.chart.title.lower() or 'revenue' in self.chart.title.lower():
            return f"${self.value:,.0f}"
        return f"{self.value:,.0f}"


class ReportSubscription(models.Model):
    """Modelo para suscripciones a reportes automáticos"""
    
    FREQUENCY_CHOICES = [
        ('daily', 'Diario'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Usuario')
    report_type = models.CharField(max_length=20, choices=Report.REPORT_TYPES, verbose_name='Tipo de Reporte')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, verbose_name='Frecuencia')
    
    # Configuración de entrega
    email_delivery = models.BooleanField(default=True, verbose_name='Entrega por Email')
    dashboard_notification = models.BooleanField(default=True, verbose_name='Notificación en Dashboard')
    
    # Estado
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    last_sent = models.DateTimeField(null=True, blank=True, verbose_name='Último Envío')
    next_send = models.DateTimeField(null=True, blank=True, verbose_name='Próximo Envío')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
    class Meta:
        verbose_name = 'Suscripción a Reporte'
        verbose_name_plural = 'Suscripciones a Reportes'
        unique_together = ['user', 'report_type', 'frequency']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_report_type_display()} ({self.get_frequency_display()})"

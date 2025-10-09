from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
import random

User = get_user_model()


class DashboardMetric(models.Model):
    """Modelo para métricas del dashboard"""
    METRIC_TYPES = [
        ('total_properties', 'Total de Propiedades'),
        ('active_clients', 'Clientes Activos'),
        ('pending_contracts', 'Contratos Pendientes'),
        ('monthly_revenue', 'Ingresos Mensuales'),
        ('new_leads', 'Nuevos Leads'),
        ('completed_activities', 'Actividades Completadas'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nombre")
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES, verbose_name="Tipo de Métrica")
    value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor")
    previous_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Valor Anterior")
    percentage_change = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Cambio Porcentual")
    icon = models.CharField(max_length=50, default='fas fa-chart-line', verbose_name="Icono")
    color = models.CharField(max_length=20, default='primary', verbose_name="Color")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Fecha de Actualización")
    
    class Meta:
        verbose_name = "Métrica del Dashboard"
        verbose_name_plural = "Métricas del Dashboard"
        ordering = ['metric_type', 'name']
    
    def __str__(self):
        return f"{self.name}: {self.value}"
    
    def calculate_percentage_change(self):
        """Calcula el cambio porcentual respecto al valor anterior"""
        if self.previous_value and self.previous_value != 0:
            change = ((self.value - self.previous_value) / self.previous_value) * 100
            self.percentage_change = round(change, 2)
        return self.percentage_change
    
    def get_trend_color(self):
        """Retorna el color basado en la tendencia"""
        if self.percentage_change is None:
            return 'secondary'
        elif self.percentage_change > 0:
            return 'success'
        elif self.percentage_change < 0:
            return 'danger'
        else:
            return 'warning'
    
    @classmethod
    def generate_mock_data(cls):
        """Genera datos mock para el dashboard"""
        mock_metrics = [
            {
                'name': 'Total de Propiedades',
                'metric_type': 'total_properties',
                'value': 1247,
                'previous_value': 1198,
                'icon': 'fas fa-home',
                'color': 'primary'
            },
            {
                'name': 'Clientes Activos',
                'metric_type': 'active_clients',
                'value': 342,
                'previous_value': 328,
                'icon': 'fas fa-users',
                'color': 'success'
            },
            {
                'name': 'Contratos Pendientes',
                'metric_type': 'pending_contracts',
                'value': 28,
                'previous_value': 35,
                'icon': 'fas fa-file-contract',
                'color': 'warning'
            },
            {
                'name': 'Ingresos Mensuales',
                'metric_type': 'monthly_revenue',
                'value': 2450000,
                'previous_value': 2280000,
                'icon': 'fas fa-dollar-sign',
                'color': 'info'
            },
            {
                'name': 'Nuevos Leads',
                'metric_type': 'new_leads',
                'value': 89,
                'previous_value': 76,
                'icon': 'fas fa-user-plus',
                'color': 'success'
            },
            {
                'name': 'Actividades Completadas',
                'metric_type': 'completed_activities',
                'value': 156,
                'previous_value': 142,
                'icon': 'fas fa-check-circle',
                'color': 'primary'
            }
        ]
        
        for metric_data in mock_metrics:
            metric, created = cls.objects.get_or_create(
                metric_type=metric_data['metric_type'],
                defaults=metric_data
            )
            if created:
                metric.calculate_percentage_change()
                metric.save()


class ChartData(models.Model):
    """Modelo para datos de gráficos del dashboard"""
    CHART_TYPES = [
        ('line', 'Línea'),
        ('bar', 'Barras'),
        ('pie', 'Circular'),
        ('doughnut', 'Dona'),
        ('area', 'Área'),
    ]
    
    chart_name = models.CharField(max_length=100, verbose_name="Nombre del Gráfico")
    chart_type = models.CharField(max_length=20, choices=CHART_TYPES, verbose_name="Tipo de Gráfico")
    label = models.CharField(max_length=100, verbose_name="Etiqueta")
    value = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Valor")
    date = models.DateField(default=timezone.now, verbose_name="Fecha")
    color = models.CharField(max_length=20, null=True, blank=True, verbose_name="Color")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Dato de Gráfico"
        verbose_name_plural = "Datos de Gráficos"
        ordering = ['chart_name', 'date', 'label']
    
    def __str__(self):
        return f"{self.chart_name} - {self.label}: {self.value}"
    
    @classmethod
    def generate_mock_chart_data(cls):
        """Genera datos mock para gráficos"""
        # Datos para gráfico de ventas mensuales
        months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio']
        sales_data = [1800000, 2100000, 1950000, 2300000, 2450000, 2200000]
        
        for i, month in enumerate(months):
            cls.objects.get_or_create(
                chart_name='Ventas Mensuales',
                chart_type='line',
                label=month,
                defaults={
                    'value': sales_data[i],
                    'date': timezone.now().date() - timedelta(days=(len(months)-i)*30),
                    'color': '#007bff'
                }
            )
        
        # Datos para gráfico de propiedades por tipo
        property_types = [
            ('Casas', 45, '#28a745'),
            ('Departamentos', 35, '#17a2b8'),
            ('Oficinas', 12, '#ffc107'),
            ('Locales', 8, '#dc3545')
        ]
        
        for prop_type, percentage, color in property_types:
            cls.objects.get_or_create(
                chart_name='Propiedades por Tipo',
                chart_type='pie',
                label=prop_type,
                defaults={
                    'value': percentage,
                    'date': timezone.now().date(),
                    'color': color
                }
            )
        
        # Datos para actividades semanales
        days = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        activities = [25, 32, 28, 35, 42, 18, 12]
        
        for i, day in enumerate(days):
            cls.objects.get_or_create(
                chart_name='Actividades Semanales',
                chart_type='bar',
                label=day,
                defaults={
                    'value': activities[i],
                    'date': timezone.now().date() - timedelta(days=6-i),
                    'color': '#6f42c1'
                }
            )


class RecentActivity(models.Model):
    """Modelo para actividades recientes del dashboard"""
    ACTIVITY_TYPES = [
        ('property_added', 'Propiedad Agregada'),
        ('client_registered', 'Cliente Registrado'),
        ('contract_signed', 'Contrato Firmado'),
        ('meeting_scheduled', 'Reunión Programada'),
        ('lead_converted', 'Lead Convertido'),
        ('payment_received', 'Pago Recibido'),
    ]
    
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES, verbose_name="Tipo de Actividad")
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Usuario")
    icon = models.CharField(max_length=50, default='fas fa-bell', verbose_name="Icono")
    color = models.CharField(max_length=20, default='primary', verbose_name="Color")
    is_read = models.BooleanField(default=False, verbose_name="Leído")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    
    class Meta:
        verbose_name = "Actividad Reciente"
        verbose_name_plural = "Actividades Recientes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    def time_since_created(self):
        """Retorna el tiempo transcurrido desde la creación"""
        now = timezone.now()
        diff = now - self.created_at
        
        if diff.days > 0:
            return f"Hace {diff.days} día{'s' if diff.days > 1 else ''}"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"Hace {hours} hora{'s' if hours > 1 else ''}"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"Hace {minutes} minuto{'s' if minutes > 1 else ''}"
        else:
            return "Hace unos segundos"
    
    @classmethod
    def generate_mock_activities(cls):
        """Genera actividades recientes mock"""
        mock_activities = [
            {
                'activity_type': 'property_added',
                'title': 'Nueva propiedad agregada',
                'description': 'Casa en Polanco con 3 recámaras y 2.5 baños',
                'icon': 'fas fa-home',
                'color': 'success'
            },
            {
                'activity_type': 'client_registered',
                'title': 'Nuevo cliente registrado',
                'description': 'María González se registró como cliente potencial',
                'icon': 'fas fa-user-plus',
                'color': 'info'
            },
            {
                'activity_type': 'contract_signed',
                'title': 'Contrato firmado',
                'description': 'Contrato de venta para departamento en Roma Norte',
                'icon': 'fas fa-file-signature',
                'color': 'primary'
            },
            {
                'activity_type': 'meeting_scheduled',
                'title': 'Reunión programada',
                'description': 'Cita con cliente para visita de propiedad mañana a las 10:00 AM',
                'icon': 'fas fa-calendar-alt',
                'color': 'warning'
            },
            {
                'activity_type': 'payment_received',
                'title': 'Pago recibido',
                'description': 'Enganche de $500,000 MXN para casa en Satelite',
                'icon': 'fas fa-money-bill-wave',
                'color': 'success'
            }
        ]
        
        for i, activity_data in enumerate(mock_activities):
            cls.objects.get_or_create(
                title=activity_data['title'],
                defaults={
                    **activity_data,
                    'created_at': timezone.now() - timedelta(hours=i*2)
                }
            )

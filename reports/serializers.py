from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Report, ReportChart, ReportData, ReportSubscription

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para usuarios"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class ReportDataSerializer(serializers.ModelSerializer):
    """Serializer para datos de gráficos"""
    formatted_value = serializers.SerializerMethodField()
    
    class Meta:
        model = ReportData
        fields = [
            'id', 'label', 'value', 'formatted_value', 'color',
            'series_name', 'date', 'order'
        ]
    
    def get_formatted_value(self, obj):
        return obj.get_formatted_value()


class ReportChartSerializer(serializers.ModelSerializer):
    """Serializer para gráficos de reportes"""
    data = ReportDataSerializer(many=True, read_only=True)
    chart_type_display = serializers.CharField(source='get_chart_type_display', read_only=True)
    
    class Meta:
        model = ReportChart
        fields = [
            'id', 'title', 'chart_type', 'chart_type_display', 'description',
            'x_axis_label', 'y_axis_label', 'show_legend', 'show_grid',
            'order', 'is_active', 'data', 'created_at'
        ]


class ReportSerializer(serializers.ModelSerializer):
    """Serializer completo para reportes"""
    created_by = UserBasicSerializer(read_only=True)
    charts = ReportChartSerializer(many=True, read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    period_display_extended = serializers.CharField(source='get_period_display_extended', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.CharField(source='get_status_color', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type', 'report_type_display', 'period', 
            'period_display', 'period_display_extended', 'start_date', 'end_date',
            'status', 'status_display', 'status_color', 'description',
            'total_records', 'file_size', 'created_by', 'created_at', 'updated_at',
            'expires_at', 'is_public', 'auto_refresh', 'is_expired',
            'days_since_created', 'charts'
        ]
    
    def get_days_since_created(self, obj):
        """Calcula los días desde la creación"""
        delta = timezone.now() - obj.created_at
        return delta.days


class ReportCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear reportes"""
    
    class Meta:
        model = Report
        fields = [
            'name', 'report_type', 'period', 'start_date', 'end_date',
            'description', 'is_public', 'auto_refresh'
        ]
    
    def validate(self, data):
        """Validaciones personalizadas"""
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
        
        if data['end_date'] > timezone.now().date():
            raise serializers.ValidationError("La fecha de fin no puede ser futura.")
        
        return data
    
    def create(self, validated_data):
        """Crea un reporte con datos mock"""
        validated_data['created_by'] = self.context['request'].user
        validated_data['total_records'] = 150  # Mock data
        validated_data['file_size'] = "2.5 MB"  # Mock data
        return super().create(validated_data)


class ReportUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar reportes"""
    
    class Meta:
        model = Report
        fields = [
            'name', 'description', 'is_public', 'auto_refresh', 'status'
        ]


class ReportListSerializer(serializers.ModelSerializer):
    """Serializer optimizado para listados de reportes"""
    created_by = UserBasicSerializer(read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_color = serializers.CharField(source='get_status_color', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    charts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'name', 'report_type', 'report_type_display', 'period',
            'period_display', 'start_date', 'end_date', 'status', 'status_display',
            'status_color', 'total_records', 'file_size', 'created_by',
            'created_at', 'is_public', 'is_expired', 'charts_count'
        ]
    
    def get_charts_count(self, obj):
        """Cuenta los gráficos del reporte"""
        return obj.charts.filter(is_active=True).count()


class ReportStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas de reportes"""
    total_reports = serializers.IntegerField()
    reports_by_type = serializers.DictField()
    reports_by_status = serializers.DictField()
    reports_by_period = serializers.DictField()
    recent_reports = ReportListSerializer(many=True)
    popular_types = serializers.ListField()
    avg_records_per_report = serializers.FloatField()


class ReportChartCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear gráficos"""
    
    class Meta:
        model = ReportChart
        fields = [
            'title', 'chart_type', 'description', 'x_axis_label',
            'y_axis_label', 'show_legend', 'show_grid', 'order'
        ]


class ReportDataCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear datos de gráficos"""
    
    class Meta:
        model = ReportData
        fields = [
            'label', 'value', 'color', 'series_name', 'date', 'order'
        ]


class ReportSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer para suscripciones a reportes"""
    user = UserBasicSerializer(read_only=True)
    report_type_display = serializers.CharField(source='get_report_type_display', read_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    
    class Meta:
        model = ReportSubscription
        fields = [
            'id', 'user', 'report_type', 'report_type_display', 'frequency',
            'frequency_display', 'email_delivery', 'dashboard_notification',
            'is_active', 'last_sent', 'next_send', 'created_at'
        ]


class ReportSubscriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear suscripciones"""
    
    class Meta:
        model = ReportSubscription
        fields = [
            'report_type', 'frequency', 'email_delivery', 'dashboard_notification'
        ]
    
    def create(self, validated_data):
        """Crea una suscripción para el usuario actual"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class ReportGenerateSerializer(serializers.Serializer):
    """Serializer para generar reportes con datos mock"""
    report_type = serializers.ChoiceField(choices=Report.REPORT_TYPES)
    period = serializers.ChoiceField(choices=Report.PERIODS)
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    include_charts = serializers.BooleanField(default=True)
    chart_types = serializers.ListField(
        child=serializers.ChoiceField(choices=ReportChart.CHART_TYPES),
        required=False
    )
    
    def validate(self, data):
        """Validaciones para generación de reportes"""
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
        
        return data


class ReportExportSerializer(serializers.Serializer):
    """Serializer para exportar reportes"""
    format = serializers.ChoiceField(choices=[
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
        ('json', 'JSON')
    ])
    include_charts = serializers.BooleanField(default=True)
    include_raw_data = serializers.BooleanField(default=False)


class ReportSearchSerializer(serializers.Serializer):
    """Serializer para búsqueda de reportes"""
    query = serializers.CharField(max_length=200)
    report_type = serializers.ChoiceField(choices=Report.REPORT_TYPES, required=False)
    status = serializers.ChoiceField(choices=Report.STATUS_CHOICES, required=False)
    period = serializers.ChoiceField(choices=Report.PERIODS, required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    created_by = serializers.IntegerField(required=False)
    is_public = serializers.BooleanField(required=False)
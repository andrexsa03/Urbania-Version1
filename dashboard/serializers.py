from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import DashboardMetric, ChartData, RecentActivity

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Serializer básico para información de usuario"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class DashboardMetricSerializer(serializers.ModelSerializer):
    """Serializer para métricas del dashboard"""
    percentage_change = serializers.SerializerMethodField()
    trend_color = serializers.SerializerMethodField()
    formatted_value = serializers.SerializerMethodField()
    formatted_previous_value = serializers.SerializerMethodField()
    
    class Meta:
        model = DashboardMetric
        fields = [
            'id', 'name', 'metric_type', 'value', 'previous_value',
            'percentage_change', 'icon', 'color', 'trend_color',
            'formatted_value', 'formatted_previous_value', 'is_active',
            'created_at', 'updated_at'
        ]
    
    def get_percentage_change(self, obj):
        return obj.calculate_percentage_change()
    
    def get_trend_color(self, obj):
        return obj.get_trend_color()
    
    def get_formatted_value(self, obj):
        """Formatea el valor según el tipo de métrica"""
        if obj.metric_type == 'monthly_revenue':
            return f"${obj.value:,.0f}"
        elif obj.metric_type in ['total_properties', 'active_clients', 'pending_contracts', 'new_leads', 'completed_activities']:
            return f"{obj.value:,.0f}"
        else:
            return str(obj.value)
    
    def get_formatted_previous_value(self, obj):
        """Formatea el valor anterior según el tipo de métrica"""
        if obj.previous_value is None:
            return None
        
        if obj.metric_type == 'monthly_revenue':
            return f"${obj.previous_value:,.0f}"
        elif obj.metric_type in ['total_properties', 'active_clients', 'pending_contracts', 'new_leads', 'completed_activities']:
            return f"{obj.previous_value:,.0f}"
        else:
            return str(obj.previous_value)


class ChartDataSerializer(serializers.ModelSerializer):
    """Serializer para datos de gráficos"""
    formatted_value = serializers.SerializerMethodField()
    
    class Meta:
        model = ChartData
        fields = [
            'id', 'chart_name', 'chart_type', 'label', 'value',
            'formatted_value', 'date', 'color', 'is_active', 'created_at'
        ]
    
    def get_formatted_value(self, obj):
        """Formatea el valor según el tipo de gráfico"""
        if obj.chart_name == 'Ventas Mensuales':
            return f"${obj.value:,.0f}"
        elif obj.chart_name == 'Propiedades por Tipo':
            return f"{obj.value}%"
        else:
            return f"{obj.value:,.0f}"


class RecentActivitySerializer(serializers.ModelSerializer):
    """Serializer para actividades recientes"""
    user = UserBasicSerializer(read_only=True)
    time_since = serializers.SerializerMethodField()
    
    class Meta:
        model = RecentActivity
        fields = [
            'id', 'activity_type', 'title', 'description', 'user',
            'icon', 'color', 'is_read', 'time_since', 'created_at'
        ]
    
    def get_time_since(self, obj):
        return obj.time_since_created()


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer para resumen completo del dashboard"""
    metrics = DashboardMetricSerializer(many=True, read_only=True)
    charts = serializers.SerializerMethodField()
    recent_activities = RecentActivitySerializer(many=True, read_only=True)
    summary_stats = serializers.SerializerMethodField()
    
    def get_charts(self, obj):
        """Organiza los datos de gráficos por nombre de gráfico"""
        charts_data = {}
        
        # Obtener todos los datos de gráficos activos
        chart_data = ChartData.objects.filter(is_active=True).order_by('chart_name', 'date', 'label')
        
        for data in chart_data:
            chart_name = data.chart_name
            if chart_name not in charts_data:
                charts_data[chart_name] = {
                    'name': chart_name,
                    'type': data.chart_type,
                    'data': []
                }
            
            charts_data[chart_name]['data'].append({
                'label': data.label,
                'value': float(data.value),
                'formatted_value': ChartDataSerializer().get_formatted_value(data),
                'color': data.color,
                'date': data.date
            })
        
        return list(charts_data.values())
    
    def get_summary_stats(self, obj):
        """Estadísticas de resumen del dashboard"""
        from django.db.models import Count, Sum, Avg
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        
        return {
            'total_metrics': DashboardMetric.objects.filter(is_active=True).count(),
            'total_charts': ChartData.objects.values('chart_name').distinct().count(),
            'unread_activities': RecentActivity.objects.filter(is_read=False).count(),
            'activities_this_week': RecentActivity.objects.filter(
                created_at__date__gte=week_ago
            ).count(),
            'last_updated': timezone.now()
        }


class MetricUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar métricas"""
    
    class Meta:
        model = DashboardMetric
        fields = ['value', 'previous_value', 'icon', 'color', 'is_active']
    
    def update(self, instance, validated_data):
        # Si se actualiza el valor, mover el valor actual a previous_value
        if 'value' in validated_data and validated_data['value'] != instance.value:
            instance.previous_value = instance.value
        
        instance = super().update(instance, validated_data)
        instance.calculate_percentage_change()
        instance.save()
        return instance


class ActivityMarkReadSerializer(serializers.ModelSerializer):
    """Serializer para marcar actividades como leídas"""
    
    class Meta:
        model = RecentActivity
        fields = ['is_read']


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer para estadísticas específicas del dashboard"""
    period = serializers.CharField(default='month')
    
    def to_representation(self, instance):
        from django.db.models import Count, Sum, Avg
        from django.utils import timezone
        from datetime import timedelta
        
        period = self.initial_data.get('period', 'month')
        today = timezone.now().date()
        
        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        elif period == 'quarter':
            start_date = today - timedelta(days=90)
        else:
            start_date = today - timedelta(days=30)
        
        # Métricas por período
        metrics = DashboardMetric.objects.filter(is_active=True)
        activities = RecentActivity.objects.filter(created_at__date__gte=start_date)
        
        return {
            'period': period,
            'start_date': start_date,
            'end_date': today,
            'metrics_summary': {
                'total_active_metrics': metrics.count(),
                'metrics_with_positive_trend': metrics.filter(percentage_change__gt=0).count(),
                'metrics_with_negative_trend': metrics.filter(percentage_change__lt=0).count(),
                'average_growth': metrics.exclude(percentage_change__isnull=True).aggregate(
                    avg_growth=Avg('percentage_change')
                )['avg_growth'] or 0
            },
            'activities_summary': {
                'total_activities': activities.count(),
                'unread_activities': activities.filter(is_read=False).count(),
                'activities_by_type': activities.values('activity_type').annotate(
                    count=Count('id')
                ).order_by('-count')
            },
            'charts_summary': {
                'total_charts': ChartData.objects.values('chart_name').distinct().count(),
                'total_data_points': ChartData.objects.filter(is_active=True).count()
            }
        }
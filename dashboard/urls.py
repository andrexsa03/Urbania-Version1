from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.DashboardSummaryView.as_view(), name='dashboard-summary'),
    
    # Métricas
    path('metricas/', views.MetricsListView.as_view(), name='metrics-list'),
    path('metricas/<int:pk>/', views.MetricDetailView.as_view(), name='metric-detail'),
    
    # Gráficos
    path('graficos/', views.ChartsDataView.as_view(), name='charts-data'),
    
    # Actividades recientes
    path('actividades/', views.RecentActivitiesView.as_view(), name='recent-activities'),
    path('actividades/<int:pk>/marcar-leida/', views.ActivityMarkReadView.as_view(), name='activity-mark-read'),
    path('actividades/marcar-todas-leidas/', views.mark_all_activities_read, name='mark-all-activities-read'),
    
    # Estadísticas y datos
    path('estadisticas/', views.dashboard_stats, name='dashboard-stats'),
    path('estadisticas-rapidas/', views.quick_stats, name='quick-stats'),
    
    # Utilidades
    path('buscar/', views.DashboardSearchView.as_view(), name='dashboard-search'),
    path('generar-datos-mock/', views.generate_mock_data, name='generate-mock-data'),
]
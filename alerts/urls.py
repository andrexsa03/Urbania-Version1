from django.urls import path
from . import views

app_name = 'alerts'

urlpatterns = [
    # Alertas principales
    path('', views.AlertListCreateView.as_view(), name='alert-list-create'),
    path('<int:pk>/', views.AlertDetailView.as_view(), name='alert-detail'),
    
    # Acciones específicas de alertas
    path('<int:pk>/read/', views.mark_alert_read, name='alert-mark-read'),
    path('<int:pk>/dismiss/', views.dismiss_alert, name='alert-dismiss'),
    
    # Plantillas de alertas
    path('templates/', views.AlertTemplateListCreateView.as_view(), name='template-list-create'),
    path('templates/<int:pk>/', views.AlertTemplateDetailView.as_view(), name='template-detail'),
    
    # Reglas de alertas
    path('rules/', views.AlertRuleListCreateView.as_view(), name='rule-list-create'),
    path('rules/<int:pk>/', views.AlertRuleDetailView.as_view(), name='rule-detail'),
    
    # Estadísticas y métricas
    path('stats/', views.alert_stats, name='alert-stats'),
    
    # Acciones en lote
    path('bulk-actions/', views.bulk_alert_actions, name='bulk-actions'),
    
    # Búsqueda y filtros
    path('search/', views.search_alerts, name='search-alerts'),
    path('active/', views.my_active_alerts, name='active-alerts'),
    path('upcoming/', views.upcoming_alerts, name='upcoming-alerts'),
    
    # Utilidades
    path('generate-mock/', views.generate_mock_alerts, name='generate-mock'),
    path('clear-all/', views.clear_all_alerts, name='clear-all'),
]
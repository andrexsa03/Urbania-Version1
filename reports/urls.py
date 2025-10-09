from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Reportes principales
    path('', views.ReportListCreateView.as_view(), name='report-list-create'),
    path('<int:pk>/', views.ReportDetailView.as_view(), name='report-detail'),
    
    # Gráficos de reportes
    path('<int:report_id>/charts/', views.ReportChartListView.as_view(), name='report-charts'),
    
    # Suscripciones
    path('subscriptions/', views.ReportSubscriptionListView.as_view(), name='subscription-list-create'),
    path('subscriptions/<int:pk>/', views.ReportSubscriptionDetailView.as_view(), name='subscription-detail'),
    
    # Estadísticas y análisis
    path('stats/', views.report_stats, name='report-stats'),
    
    # Generación de reportes
    path('generate/', views.generate_report, name='generate-report'),
    
    # Exportación
    path('<int:pk>/export/', views.export_report, name='export-report'),
    
    # Búsqueda
    path('search/', views.search_reports, name='search-reports'),
    
    # Reportes específicos del usuario
    path('my-reports/', views.my_reports, name='my-reports'),
    path('public/', views.public_reports, name='public-reports'),
    
    # Datos mock para pruebas
    path('generate-mock/', views.generate_mock_data, name='generate-mock-data'),
]
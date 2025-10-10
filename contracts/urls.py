from django.urls import path
from . import views

app_name = 'contracts'

urlpatterns = [
    # Endpoints principales de contratos
    path('', views.ContractListCreateView.as_view(), name='contract-list-create'),
    path('<int:pk>/', views.ContractDetailView.as_view(), name='contract-detail'),
    
    # Endpoints para pagos de contratos
    path('<int:contract_id>/payments/', views.ContractPaymentListCreateView.as_view(), name='contract-payments'),
    
    # Endpoints para documentos de contratos
    path('<int:contract_id>/documents/', views.ContractDocumentListCreateView.as_view(), name='contract-documents'),
    
    # Endpoints para notas de contratos
    path('<int:contract_id>/notes/', views.ContractNoteListCreateView.as_view(), name='contract-notes'),
    
    # Endpoints de estadísticas y reportes
    path('stats/', views.contract_stats, name='contract-stats'),
    path('summary-by-agent/', views.contract_summary_by_agent, name='contract-summary-by-agent'),
    
    # Endpoints de acciones específicas
    path('<int:pk>/update-status/', views.update_contract_status, name='update-contract-status'),
    path('bulk-actions/', views.bulk_contract_actions, name='bulk-contract-actions'),
    
    # Endpoints de búsqueda y filtros
    path('search/', views.search_contracts, name='search-contracts'),
    path('my-contracts/', views.my_contracts, name='my-contracts'),
    path('expiring/', views.expiring_contracts, name='expiring-contracts'),
    
    # Endpoints de utilidades
    path('generate-mock/', views.generate_mock_contracts, name='generate-mock-contracts'),
    path('clear-user-contracts/', views.clear_user_contracts, name='clear-user-contracts'),
]
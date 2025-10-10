from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Vista de chat HTML (para testing)
    path('chat/<int:conversation_id>/', views.chat_view, name='chat'),
    
    # API Endpoints para conversaciones
    path('conversaciones/', views.ConversationListCreateView.as_view(), name='conversation-list'),
    path('conversaciones/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    
    # API Endpoints para mensajes
    path('conversaciones/<int:conversation_id>/mensajes/', views.MessageListCreateView.as_view(), name='message-list'),
    path('conversaciones/<int:conversation_id>/mensajes/<int:pk>/', views.MessageDetailView.as_view(), name='message-detail'),
    
    # API Endpoints para reacciones
    path('conversaciones/<int:conversation_id>/mensajes/<int:message_id>/reacciones/', views.add_reaction, name='add-reaction'),
    path('conversaciones/<int:conversation_id>/mensajes/<int:message_id>/reacciones/eliminar/', views.remove_reaction, name='remove-reaction'),
    
    # API Endpoints para búsqueda y estadísticas
    path('buscar/', views.search_messages, name='search-messages'),
    path('estadisticas/', views.message_stats, name='message-stats'),
    
    # API Endpoints para estado de usuarios
    path('estado/', views.user_status, name='user-status'),
    path('usuarios-en-linea/', views.online_users, name='online-users'),
    
    # Endpoints para desarrollo (solo en DEBUG=True)
    path('dev/generar-mensajes/', views.generate_mock_messages, name='generate-mock-messages'),
    path('dev/limpiar-mensajes/', views.clear_user_messages, name='clear-user-messages'),
]
"""
WebSocket URL routing for Django Channels
"""

from django.urls import path
from messaging import consumers

websocket_urlpatterns = [
    path('ws/chat/<int:conversation_id>/', consumers.ChatConsumer.as_asgi()),
    path('ws/notifications/', consumers.NotificationConsumer.as_asgi()),
    path('ws/user-status/', consumers.UserStatusConsumer.as_asgi()),
]
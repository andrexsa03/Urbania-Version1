from django.urls import path
from . import views

app_name = 'navigation'

urlpatterns = [
    # Navegación principal
    path('menu/', views.NavigationMenuView.as_view(), name='navigation-menu'),
    path('current-section/', views.UpdateCurrentSectionView.as_view(), name='update-current-section'),
    path('stats/', views.navigation_stats, name='navigation-stats'),
    
    # Notificaciones
    path('notifications/', views.NotificationListView.as_view(), name='notification-list'),
    path('notifications/mark-read/', views.NotificationMarkReadView.as_view(), name='mark-notifications-read'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
]
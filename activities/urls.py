from django.urls import path
from . import views

app_name = 'activities'

urlpatterns = [
    # CRUD principal de actividades
    path('', views.ActivityListCreateView.as_view(), name='activity-list-create'),
    path('<int:pk>/', views.ActivityDetailView.as_view(), name='activity-detail'),
    path('<int:pk>/complete/', views.ActivityMarkCompleteView.as_view(), name='activity-complete'),
    
    # Endpoints especializados
    path('stats/', views.activity_stats, name='activity-stats'),
    path('pending/', views.pending_activities, name='pending-activities'),
    path('overdue/', views.overdue_activities, name='overdue-activities'),
    path('today/', views.today_activities, name='today-activities'),
]
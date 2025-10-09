"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger/OpenAPI schema configuration
schema_view = get_schema_view(
    openapi.Info(
        title="URBANY Authentication API",
        default_version='v1',
        description="Sistema de autenticación completo con Django REST Framework",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@urbany.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    
    # API endpoints
    path('api/', include('rest_framework.urls')),
    
    # Authentication endpoints
    path('api/auth/', include('authentication.urls')),
    
    # User management endpoints
    path('api/users/', include('users.urls')),
    
    # Role management endpoints
    path('api/roles/', include('roles.urls')),
    
    # Navigation API
    path('api/navegacion/', include('navigation.urls')),
    
    # Activities API
    path('api/actividades/', include('activities.urls')),
    
    # Dashboard
    path('api/dashboard/', include('dashboard.urls')),
    
    # Reports
    path('api/reportes/', include('reports.urls')),
    
    # Alerts
    path('api/alertas/', include('alerts.urls')),
    
    # Contracts
    path('api/contratos/', include('contracts.urls')),
    
    # Messaging
    path('api/mensajes/', include('messaging.urls')),
    
    # API Documentation endpoints
    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='api-schema'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='api-docs'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='api-redoc'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


#En este apartado se colocaran los Endpoints de la API
# path('api/v1/your-app/', include('apps.your_app.urls')),
#!Recordatorio - Los Endpoints se separan por modulo
#!Recordatorio - Los Endpoints se documentan por funciones en un archivo ENDPOINTS.md
#!Recordatorio - Los Endpoints se comentan de igual manera

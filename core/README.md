# Aplicación Core (Núcleo del Sistema)

## Propósito
La aplicación `core` constituye el núcleo central del sistema URBANY CRM. Contiene la configuración principal de Django, la configuración de URLs globales, y los ajustes fundamentales que permiten el funcionamiento coordinado de todas las aplicaciones del sistema.

## Funciones Principales

### 1. Configuración Central del Sistema
- **Archivo**: `settings.py`
- **Propósito**: Configuración global de Django y todas las aplicaciones
- **Funcionalidad**: Define parámetros de base de datos, seguridad, aplicaciones instaladas

### 2. Enrutamiento Global
- **Archivo**: `urls.py`
- **Propósito**: Configuración de URLs principales del sistema
- **Funcionalidad**: Incluye URLs de todas las aplicaciones y documentación API

### 3. Configuración WSGI/ASGI
- **Archivos**: `wsgi.py`, `asgi.py`
- **Propósito**: Configuración para servidores web
- **Funcionalidad**: Interfaces para despliegue en producción

## Archivos y Componentes

### `settings.py`
Configuración principal del proyecto Django:

#### Configuración de Base de Datos
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

#### Aplicaciones Instaladas
- **Django Apps**: Aplicaciones core de Django
- **Third Party**: DRF, JWT, CORS, etc.
- **Local Apps**: `authentication`, `users`, `roles`

#### Configuración de Seguridad
- **SECRET_KEY**: Clave secreta para operaciones criptográficas
- **DEBUG**: Modo de desarrollo/producción
- **ALLOWED_HOSTS**: Hosts permitidos para el sistema
- **CORS_SETTINGS**: Configuración de Cross-Origin Resource Sharing

#### Configuración de REST Framework
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20
}
```

#### Configuración JWT
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

#### Configuración de Swagger/OpenAPI
```python
SPECTACULAR_SETTINGS = {
    'TITLE': 'URBANY CRM API',
    'DESCRIPTION': 'Sistema de gestión de relaciones con clientes',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
```

### `urls.py`
Configuración de URLs principales:

#### Rutas de Aplicaciones
- `/api/auth/` → Aplicación de autenticación
- `/api/users/` → Aplicación de usuarios
- `/api/roles/` → Aplicación de roles

#### Documentación API
- `/api/schema/` → Esquema OpenAPI
- `/api/docs/` → Documentación Swagger UI
- `/api/redoc/` → Documentación ReDoc

#### Configuración de Rutas
```python
urlpatterns = [
    path('api/auth/', include('authentication.urls', namespace='authentication')),
    path('api/users/', include('users.urls', namespace='users')),
    path('api/roles/', include('roles.urls', namespace='roles')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

### `wsgi.py`
Configuración WSGI para despliegue:
- **Propósito**: Interface para servidores web WSGI
- **Uso**: Despliegue en servidores como Apache, Nginx + Gunicorn
- **Configuración**: Apunta a `core.settings`

### `asgi.py`
Configuración ASGI para aplicaciones asíncronas:
- **Propósito**: Interface para servidores ASGI
- **Uso**: Soporte para WebSockets, aplicaciones asíncronas
- **Configuración**: Preparado para funcionalidades futuras

## Configuraciones Específicas

### Seguridad
```python
# Configuración de seguridad
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Internacionalización
```python
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True
```

### Archivos Estáticos y Media
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### Logging
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'urbany_crm.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

## Variables de Entorno

### Archivo `.env.example`
Template para configuración de entorno:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Variables Críticas
- **SECRET_KEY**: Clave secreta para operaciones criptográficas
- **DEBUG**: Modo de desarrollo (False en producción)
- **DATABASE_URL**: URL de conexión a base de datos
- **EMAIL_SETTINGS**: Configuración para envío de emails

## Dependencias Principales

### Django Core
- `Django>=4.2.0`: Framework web principal
- `djangorestframework>=3.14.0`: Framework para APIs REST
- `django-cors-headers>=4.0.0`: Manejo de CORS

### Autenticación y Seguridad
- `djangorestframework-simplejwt>=5.2.0`: Tokens JWT
- `django-environ>=0.10.0`: Gestión de variables de entorno

### Documentación API
- `drf-spectacular>=0.26.0`: Generación de documentación OpenAPI

### Base de Datos
- `sqlite3`: Base de datos por defecto (incluida en Python)
- Preparado para PostgreSQL, MySQL en producción

## Configuración de Desarrollo vs Producción

### Desarrollo
```python
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
CORS_ALLOW_ALL_ORIGINS = True
```

### Producción
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
CORS_ALLOWED_ORIGINS = ['https://yourdomain.com']
SECURE_SSL_REDIRECT = True
```

## Comandos de Gestión

### Desarrollo
```bash
# Iniciar servidor de desarrollo
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar pruebas
python manage.py test
```

### Producción
```bash
# Recopilar archivos estáticos
python manage.py collectstatic

# Verificar configuración
python manage.py check --deploy

# Crear respaldo de base de datos
python manage.py dumpdata > backup.json
```

## Monitoreo y Logging

### Archivos de Log
- `urbany_crm.log`: Log principal del sistema
- `django.log`: Logs específicos de Django
- `api.log`: Logs de peticiones API

### Métricas Disponibles
- Tiempo de respuesta de APIs
- Errores de autenticación
- Uso de endpoints
- Estadísticas de usuarios

## Notas de Desarrollo

### Estructura de Proyecto
```
core/
├── __init__.py
├── settings.py      # Configuración principal
├── urls.py         # URLs globales
├── wsgi.py         # Configuración WSGI
└── asgi.py         # Configuración ASGI
```

### Extensibilidad
- Fácil agregar nuevas aplicaciones
- Configuración modular por entorno
- Soporte para múltiples bases de datos

### Mejores Prácticas
- Usar variables de entorno para configuración sensible
- Separar configuración por entornos
- Mantener logs detallados para debugging
- Implementar monitoreo de performance

### Seguridad
- Nunca commitear SECRET_KEY
- Usar HTTPS en producción
- Configurar CORS apropiadamente
- Implementar rate limiting
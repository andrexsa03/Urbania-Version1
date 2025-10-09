# CRM URBANY

## Descripción del Proyecto

CRM URBANY es un sistema de gestión de relaciones con clientes diseñado específicamente para inmobiliarias. Permite gestionar propiedades, contactos, comunicaciones y automatizar procesos de venta inmobiliaria, mejorando la eficiencia operativa y la experiencia del cliente.

## Objetivos

- Centralizar la gestión de propiedades inmobiliarias
- Automatizar procesos de comunicación con clientes
- Integrar con plataformas de marketing y redes sociales
- Facilitar la colaboración entre agentes inmobiliarios
- Proporcionar análisis de datos para la toma de decisiones

## 🚀 Guía de Instalación y Configuración

### Prerrequisitos

- **Python 3.8+** (Recomendado: Python 3.11)
- **Git** para clonar el repositorio
- **Postman** para probar los endpoints (opcional)

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd URBANY
```

### 2. Crear y Activar Entorno Virtual

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install Django==4.2.7
pip install djangorestframework==3.14.0
pip install djangorestframework-simplejwt==5.3.0
pip install django-cors-headers==4.3.0
pip install drf-yasg==1.21.7
```

**O instalar desde requirements.txt (si está disponible):**
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crear archivo `.env` basado en `.env.example`:
```bash
cp .env.example .env
```

### 5. Ejecutar Migraciones

```bash
python manage.py migrate
```

### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

**Credenciales por defecto (para desarrollo):**
- **Email:** admin@urbany.com
- **Contraseña:** admin123
- **Nombre:** Admin
- **Apellido:** User

### 7. Iniciar el Servidor

**Para desarrollo con WebSockets:**
```bash
python manage.py runserver
```

**Para producción con Daphne:**
```bash
daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

### 8. Probar WebSockets

**Interfaz de Chat:**
- Visita: `http://127.0.0.1:8000/messaging/chat/`
- Crea una conversación y prueba el chat en tiempo real

**Endpoints WebSocket:**
- Chat: `ws://127.0.0.1:8000/ws/chat/<conversation_id>/`
- Notificaciones: `ws://127.0.0.1:8000/ws/notifications/<user_id>/`
- Estado: `ws://127.0.0.1:8000/ws/user-status/<user_id>/`

## 📋 URLs Importantes

- **API Base:** `http://127.0.0.1:8000/api/`
- **Documentación Swagger:** `http://127.0.0.1:8000/swagger/`
- **API Docs:** `http://127.0.0.1:8000/api/docs/`
- **Panel Admin:** `http://127.0.0.1:8000/admin/`
- **Health Check:** `http://127.0.0.1:8000/api/auth/health/`
- **Chat Interface:** `http://127.0.0.1:8000/messaging/chat/`

### WebSocket URLs
- **Chat:** `ws://127.0.0.1:8000/ws/chat/<conversation_id>/`
- **Notificaciones:** `ws://127.0.0.1:8000/ws/notifications/<user_id>/`
- **Estado Usuario:** `ws://127.0.0.1:8000/ws/user-status/<user_id>/`

## 🔧 Configuración para Postman

### Variables de Entorno
```json
{
  "base_url": "http://127.0.0.1:8000",
  "access_token": "",
  "refresh_token": "",
  "user_id": ""
}
```

### Headers Globales
- `Content-Type: application/json`
- `Authorization: Bearer {{access_token}}`

## 🧪 Verificación de Instalación

### 1. Verificar Health Check
```bash
curl http://127.0.0.1:8000/api/auth/health/
```

### 2. Probar Registro de Usuario
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 3. Probar Login
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@urbany.com",
    "password": "admin123"
  }'
```

## Estado Actual del Proyecto - MODULO 01

**Versión**: 1.0.0 (Desarrollo)  
**Última Actualización**: Enero 2025

### Cambios Recientes Implementados

#### 🔧 Modificaciones Estructurales
- **Limpieza de Código**: Eliminación de archivos no esenciales (`admin.py` vacíos, `models.py` sin funcionalidad)
- **Optimización de Aplicaciones**: Mantenimiento solo del código esencial en cada aplicación
- **Documentación Completa**: Cada aplicación ahora cuenta con documentación detallada de su propósito y funcionalidades

#### 🗄️ Base de Datos
- **Nueva Tabla de Testing**: Creación de tabla `usuarios` en SQLite3 para pruebas del sistema de login
  - Campos: `id` (INTEGER PRIMARY KEY), `usuario` (TEXT UNIQUE), `contraseña` (TEXT), `fecha_creacion` (TIMESTAMP)
  - Incluye medidas de seguridad básicas para almacenamiento de credenciales
  - Usuario de prueba preconfigurado para testing

#### 🏗️ Arquitectura Actual
El sistema está implementado con Django REST Framework y consta de las siguientes aplicaciones:

1. **Core** (`core/`): Configuración central del sistema
2. **Authentication** (`authentication/`): Sistema de autenticación JWT
3. **Users** (`users/`): Gestión de usuarios y perfiles
4. **Roles** (`roles/`): Sistema de roles y permisos

## Aplicaciones Implementadas

### 1. Aplicación Core
**Ubicación**: `core/`  
**Propósito**: Núcleo central del sistema con configuración global

**Funcionalidades**:
- Configuración de Django y DRF
- Enrutamiento global de URLs
- Configuración de seguridad y JWT
- Configuración de base de datos SQLite3
- Documentación automática con Swagger/OpenAPI

### 2. Aplicación Authentication
**Ubicación**: `authentication/`  
**Propósito**: Gestión completa de autenticación de usuarios

**Funcionalidades**:
- Registro de usuarios con validación de email
- Login con tokens JWT (access/refresh)
- Recuperación de contraseñas
- Autenticación de dos factores (2FA)
- Health check del sistema

### 3. Aplicación Users
**Ubicación**: `users/`  
**Propósito**: Gestión de usuarios y perfiles

**Funcionalidades**:
- Modelo de usuario extendido con campos personalizados
- Gestión de perfiles de usuario
- Cambio de contraseñas
- Asignación de roles
- Estadísticas de usuarios

### 4. Aplicación Roles
**Ubicación**: `roles/`  
**Propósito**: Sistema de roles y permisos

**Funcionalidades**:
- CRUD de roles y permisos
- Asignación de permisos a roles
- Gestión de usuarios por rol
- Estadísticas de roles y permisos

## Módulos y Equipos Responsables

El proyecto está dividido en 4 módulos principales:

## Módulo 1: Autenticación y Gestión de Usuarios

### Descripción General
Sistema encargado de todos los procesos de autenticación, registro y administración de usuarios en el CRM URBANY.

### Arquitectura y Componentes Principales
- **Sistema de Autenticación**: Gestiona login, registro y recuperación de contraseñas
- **Gestión de Usuarios**: Administra perfiles y datos personales
- **Sistema de Roles**: Implementa permisos y roles de usuario
- **API REST**: Proporciona endpoints para operaciones de usuario

### Dependencias y Requisitos
- Django 4.2+
- Django REST Framework
- JWT para autenticación
- PostgreSQL para almacenamiento de datos
- Módulo 4 para gestión de permisos en redes inmobiliarias

### Estructura de Directorios
```
modulo1/
├── auth/                  # Componentes de autenticación
├── users/                 # Gestión de usuarios
├── roles/                 # Sistema de roles
└── api/                   # Endpoints de API
```

### Configuración Necesaria
- Configuración de base de datos PostgreSQL
- Configuración de JWT para tokens de autenticación
- Configuración de permisos y roles iniciales

### Equipo Responsable
Backend 1

## Módulo 5: Sistema de Mensajería en Tiempo Real

### Descripción General
Sistema de comunicación en tiempo real que permite chat entre usuarios, notificaciones instantáneas y seguimiento de estado de usuarios.

### Arquitectura y Componentes Principales
- **Django Channels**: Framework para WebSockets y comunicación asíncrona
- **WebSocket Consumers**: Manejadores de conexiones WebSocket
- **Channel Layers**: Sistema de mensajería entre procesos
- **Sistema de Chat**: Chat en tiempo real entre usuarios
- **Notificaciones**: Sistema de notificaciones instantáneas
- **Estado de Usuario**: Seguimiento de estado online/offline

### Funcionalidades Implementadas
- **Chat en Tiempo Real**: Mensajería instantánea entre usuarios
- **Indicadores de Escritura**: Notificación cuando un usuario está escribiendo
- **Confirmaciones de Lectura**: Seguimiento de mensajes leídos
- **Reacciones a Mensajes**: Sistema de reacciones (like, love, etc.)
- **Estado de Usuario**: Seguimiento de estado online/offline/ausente
- **Notificaciones Automáticas**: Notificaciones de nuevos mensajes y actividades

### WebSocket Endpoints
- `ws://localhost:8000/ws/chat/<conversation_id>/` - Chat en tiempo real
- `ws://localhost:8000/ws/notifications/<user_id>/` - Notificaciones instantáneas
- `ws://localhost:8000/ws/user-status/<user_id>/` - Estado de usuario

### Dependencias y Requisitos
- Django Channels 4.0+
- Daphne (servidor ASGI)
- Redis para Channel Layers (opcional, usa in-memory para desarrollo)
- WebSocket support en el navegador

### Configuración Necesaria
- Configuración ASGI en lugar de WSGI
- Channel Layers configurado
- Routing de WebSockets
- Consumers implementados

### Equipo Responsable
Backend 4

## Módulo 2: Gestión de Propiedades

### Descripción General
Módulo que maneja la creación, edición y publicación de propiedades inmobiliarias en el sistema.

### Arquitectura y Componentes Principales
- **Gestión de Propiedades**: Administra datos básicos de propiedades
- **Sistema Multimedia**: Gestiona imágenes y documentos
- **Motor de Búsqueda**: Implementa búsqueda y filtrado avanzado
- **API REST**: Proporciona endpoints para operaciones con propiedades

### Dependencias y Requisitos
- Django 4.2+
- Django REST Framework
- PostgreSQL con extensión PostGIS para geolocalización
- Pillow para manejo de imágenes
- Módulo 1 para asignación de propiedades a usuarios
- Módulo 3 para promoción y publicación de propiedades

### Estructura de Directorios
```
modulo2/
├── properties/            # Gestión de propiedades
├── media/                 # Gestión de archivos multimedia
├── search/                # Sistema de búsqueda
└── api/                   # Endpoints de API
```

### Configuración Necesaria
- Configuración de almacenamiento para archivos multimedia
- Configuración de PostGIS para geolocalización
- Configuración de indexación para búsquedas

### Equipo Responsable
Backend 2

## Módulo 3: Comunicación y Marketing

### Descripción General
Módulo que gestiona todas las comunicaciones con clientes y las integraciones con plataformas de marketing.

### Arquitectura y Componentes Principales
- **Sistema de Comunicaciones**: Gestiona envío de mensajes a clientes
- **Plantillas**: Administra plantillas para diferentes tipos de comunicación
- **Integraciones Externas**: Conecta con plataformas de marketing
- **API REST**: Proporciona endpoints para operaciones de comunicación

### Dependencias y Requisitos
- Django 4.2+
- Celery para tareas asíncronas
- APIs de integración (MyPerfit, Instagram, WhatsApp)
- Redis para colas de mensajes
- Módulo 1 para información de usuarios
- Módulo 2 para datos de propiedades en campañas

### Estructura de Directorios
```
modulo3/
├── communications/        # Gestión de comunicaciones
├── templates/             # Plantillas de comunicación
├── integrations/          # Integraciones con plataformas externas
└── api/                   # Endpoints de API
```

### Configuración Necesaria
- Configuración de Celery y Redis
- Configuración de APIs externas
- Configuración de plantillas predeterminadas

### Equipo Responsable
Backend 3

## Módulo 4: Redes Inmobiliarias y Colaboración

### Descripción General
Módulo que gestiona la creación de redes inmobiliarias, invitaciones y compartición de propiedades entre agentes.

### Arquitectura y Componentes Principales
- **Gestión de Redes**: Administra redes inmobiliarias
- **Sistema de Invitaciones**: Gestiona invitaciones a redes
- **Compartición de Propiedades**: Permite compartir propiedades entre agentes
- **API REST**: Proporciona endpoints para operaciones de colaboración

### Dependencias y Requisitos
- Django 4.2+
- Django Channels para comunicación en tiempo real
- PostgreSQL para almacenamiento de datos
- WebSockets para notificaciones en tiempo real
- Módulo 1 para gestión de permisos de usuarios
- Módulo 2 para compartir propiedades

### Estructura de Directorios
```
modulo4/
├── networks/              # Gestión de redes inmobiliarias
├── invitations/           # Sistema de invitaciones
├── sharing/               # Compartición de propiedades
├── activities/            # Seguimiento de actividades
├── navigation/            # Sistema de navegación
├── dashboard/             # Panel de control
├── reports/               # Sistema de reportes
├── alerts/                # Sistema de alertas
├── contracts/             # Gestión de contratos
├── messaging/             # Sistema de mensajería en tiempo real
└── api/                   # Endpoints de API
```

### Configuración Necesaria
- Configuración de Django Channels
- Configuración de WebSockets
- Configuración de permisos de compartición

## Historias de Usuario


###  Modulo Desarrollo (Backend)
- HU01: Autenticación de usuario en el sistema CRM URBANY
- HU03: Registro de usuario individual en CRM URBANY
- HU14: Gestión de propiedades inmobiliarias
- HU16: Gestión de contactos y clientes potenciales
- HU19: Seguimiento de actividades y tareas
- HU20: Gestión de calendario y citas
- HU21: Configuración de notificaciones y alertas
- HU26: Gestión de redes inmobiliarias
- HU27: Análisis y reportes de actividad
- HU28: Configuración de permisos y roles
- HU30: Integración con APIs externas
- HU31: Gestión de documentos y archivos

### Modulos Maqueta (Simulación)
- HU02: Registro inicial de inmobiliaria en CRM URBANY
- HU04: Gestión de plantillas de email para respuestas automáticas
- HU05: Configuración de automatización para notificación de nuevas propiedades
- HU06: Integración de correo electrónico profesional con el CRM
- HU07: Integración con redes inmobiliarias para mayor alcance
- HU08: Gestión de invitaciones y creación de redes inmobiliarias
- HU09: Integración con plataformas de email marketing
- HU10: Configuración de integración con MyPerfit para Email Marketing
- HU11: Integración de redes sociales - Instagram Business y WhatsApp Business
- HU12: Configuración de integraciones oficiales y alternativas
- HU13: Configuración de integraciones con portales inmobiliarios
- HU15: Gestión de leads y oportunidades de venta
- HU17: Automatización de seguimiento de clientes
- HU18: Configuración de flujos de trabajo automatizados
- HU22: Personalización de dashboard y widgets
- HU23: Configuración de preferencias de usuario
- HU24: Gestión de equipos y colaboradores
- HU25: Configuración de marca y personalización visual

## Estructura de Directorios Actual - PROYECTO COMPLETO

```
URBANY/
├── core/                  # Configuración central del sistema
│   ├── __init__.py
│   ├── settings.py        # Configuración principal de Django
│   ├── urls.py           # URLs globales del sistema
│   ├── wsgi.py           # Configuración WSGI
│   ├── asgi.py           # Configuración ASGI para WebSockets
│   └── README.md         # Documentación del core
├── authentication/        # Sistema de autenticación
│   ├── __init__.py
│   ├── apps.py
│   ├── serializers.py    # Serializadores para autenticación
│   ├── views.py          # Vistas de autenticación (registro, login, etc.)
│   ├── urls.py           # URLs de autenticación
│   ├── tests.py          # Pruebas unitarias
│   └── README.md         # Documentación de autenticación
├── users/                 # Gestión de usuarios
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py         # Modelo de usuario extendido
│   ├── serializers.py    # Serializadores de usuario
│   ├── views.py          # Vistas de gestión de usuarios
│   ├── urls.py           # URLs de usuarios
│   ├── tests.py          # Pruebas unitarias
│   └── README.md         # Documentación de usuarios
├── roles/                 # Sistema de roles y permisos
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py         # Modelos de roles y permisos
│   ├── serializers.py    # Serializadores de roles
│   ├── views.py          # Vistas de gestión de roles
│   ├── urls.py           # URLs de roles
│   ├── tests.py          # Pruebas unitarias
│   └── README.md         # Documentación de roles
├── networks/              # Gestión de redes inmobiliarias
│   ├── models.py         # Modelos de redes
│   ├── serializers.py    # Serializadores de redes
│   ├── views.py          # Vistas de gestión de redes
│   └── urls.py           # URLs de redes
├── invitations/           # Sistema de invitaciones
│   ├── models.py         # Modelos de invitaciones
│   ├── serializers.py    # Serializadores de invitaciones
│   ├── views.py          # Vistas de gestión de invitaciones
│   └── urls.py           # URLs de invitaciones
├── sharing/               # Compartición de propiedades
│   ├── models.py         # Modelos de compartición
│   ├── serializers.py    # Serializadores de compartición
│   ├── views.py          # Vistas de gestión de compartición
│   └── urls.py           # URLs de compartición
├── activities/            # Seguimiento de actividades
│   ├── models.py         # Modelos de actividades
│   ├── serializers.py    # Serializadores de actividades
│   ├── views.py          # Vistas de gestión de actividades
│   └── urls.py           # URLs de actividades
├── navigation/            # Sistema de navegación
│   ├── models.py         # Modelos de navegación
│   ├── serializers.py    # Serializadores de navegación
│   ├── views.py          # Vistas de gestión de navegación
│   └── urls.py           # URLs de navegación
├── dashboard/             # Panel de control
│   ├── models.py         # Modelos de dashboard
│   ├── serializers.py    # Serializadores de dashboard
│   ├── views.py          # Vistas de gestión de dashboard
│   └── urls.py           # URLs de dashboard
├── reports/               # Sistema de reportes
│   ├── models.py         # Modelos de reportes
│   ├── serializers.py    # Serializadores de reportes
│   ├── views.py          # Vistas de gestión de reportes
│   └── urls.py           # URLs de reportes
├── alerts/                # Sistema de alertas
│   ├── models.py         # Modelos de alertas
│   ├── serializers.py    # Serializadores de alertas
│   ├── views.py          # Vistas de gestión de alertas
│   └── urls.py           # URLs de alertas
├── contracts/             # Gestión de contratos
│   ├── models.py         # Modelos de contratos
│   ├── serializers.py    # Serializadores de contratos
│   ├── views.py          # Vistas de gestión de contratos
│   └── urls.py           # URLs de contratos
├── messaging/             # Sistema de mensajería en tiempo real
│   ├── models.py         # Modelos de mensajería
│   ├── serializers.py    # Serializadores de mensajería
│   ├── views.py          # Vistas de gestión de mensajería
│   ├── urls.py           # URLs de mensajería
│   ├── consumers.py      # WebSocket consumers
│   ├── routing.py        # Routing de WebSockets
│   ├── channel_layers.py # Channel layers personalizados
│   └── templates/        # Plantillas de chat
├── static/                # Archivos estáticos
├── media/                 # Archivos multimedia
├── templates/             # Plantillas globales
├── db.sqlite3            # Base de datos SQLite3
├── manage.py             # Script de gestión de Django
├── requirements.txt      # Dependencias del proyecto
└── README.md             # Documentación principal (este archivo)
```

## Tecnologías Implementadas

### Backend
- **Django 4.2+**: Framework web principal
- **Django REST Framework**: Framework para APIs REST
- **Django Channels 4.0+**: Framework para WebSockets y comunicación en tiempo real
- **SQLite3**: Base de datos para desarrollo y testing
- **JWT (Simple JWT)**: Autenticación basada en tokens
- **drf-yasg**: Documentación automática de API
- **Daphne**: Servidor ASGI para WebSockets

### Comunicación en Tiempo Real
- **WebSockets**: Protocolo de comunicación bidireccional
- **ASGI**: Interface asíncrona para aplicaciones web
- **Channel Layers**: Sistema de mensajería entre procesos
- **Redis**: Backend para Channel Layers (opcional, usa in-memory para desarrollo)

### Filtros y Búsqueda
- **django-filter**: Sistema de filtros avanzados para APIs
- **DjangoFilterBackend**: Backend de filtros para DRF

### Validación y Datos
- **django-phonenumber-field**: Validación de números telefónicos
- **phonenumbers**: Librería de validación de números telefónicos

### Seguridad
- **CORS Headers**: Configuración de Cross-Origin Resource Sharing
- **JWT Authentication**: Tokens de acceso y refresh
- **Password Hashing**: Encriptación segura de contraseñas
- **Permission System**: Sistema de permisos granular

### Documentación
- **Swagger UI**: Interfaz interactiva de documentación API
- **ReDoc**: Documentación alternativa de API
- **OpenAPI Schema**: Esquema estándar de documentación

### Desarrollo y Testing
- **pytest**: Framework de testing
- **pytest-django**: Plugin de pytest para Django
- **coverage**: Análisis de cobertura de código
- **factory-boy**: Generación de datos de prueba

## APIs Disponibles

### Autenticación (`/api/auth/`)
- `POST /api/auth/register/` - Registro de usuarios
- `POST /api/auth/login/` - Inicio de sesión
- `POST /api/auth/logout/` - Cierre de sesión
- `POST /api/auth/password-recovery/` - Recuperación de contraseña
- `POST /api/auth/two-factor/` - Autenticación de dos factores
- `GET /api/auth/health/` - Estado del sistema

### Usuarios (`/api/users/`)
- `GET /api/users/` - Lista de usuarios
- `POST /api/users/` - Crear usuario
- `GET /api/users/{id}/` - Detalle de usuario
- `PUT /api/users/{id}/` - Actualizar usuario
- `DELETE /api/users/{id}/` - Eliminar usuario
- `POST /api/users/{id}/change-password/` - Cambiar contraseña
- `GET /api/users/statistics/` - Estadísticas de usuarios

### Roles (`/api/roles/`)
- `GET /api/roles/` - Lista de roles
- `POST /api/roles/` - Crear rol
- `GET /api/roles/{id}/` - Detalle de rol
- `PUT /api/roles/{id}/` - Actualizar rol
- `DELETE /api/roles/{id}/` - Eliminar rol
- `POST /api/roles/{id}/add-permission/` - Agregar permiso
- `POST /api/roles/{id}/remove-permission/` - Remover permiso
- `GET /api/roles/permissions/` - Lista de permisos
- `GET /api/roles/statistics/` - Estadísticas de roles

### Mensajería (`/api/messaging/`)
- `GET /api/messaging/conversations/` - Lista de conversaciones
- `POST /api/messaging/conversations/` - Crear conversación
- `GET /api/messaging/conversations/{id}/` - Detalle de conversación
- `GET /api/messaging/conversations/{id}/messages/` - Mensajes de conversación
- `POST /api/messaging/conversations/{id}/messages/` - Enviar mensaje
- `POST /api/messaging/messages/{id}/react/` - Reaccionar a mensaje
- `DELETE /api/messaging/messages/{id}/react/` - Quitar reacción
- `GET /api/messaging/stats/` - Estadísticas de mensajería
- `GET /api/messaging/status/` - Estado de usuario

### WebSocket Endpoints
- `ws://localhost:8000/ws/chat/<conversation_id>/` - Chat en tiempo real
- `ws://localhost:8000/ws/notifications/<user_id>/` - Notificaciones instantáneas
- `ws://localhost:8000/ws/user-status/<user_id>/` - Estado de usuario

### Redes (`/api/networks/`)
- `GET /api/networks/` - Lista de redes inmobiliarias
- `POST /api/networks/` - Crear red
- `GET /api/networks/{id}/` - Detalle de red
- `PUT /api/networks/{id}/` - Actualizar red
- `DELETE /api/networks/{id}/` - Eliminar red

### Invitaciones (`/api/invitations/`)
- `GET /api/invitations/` - Lista de invitaciones
- `POST /api/invitations/` - Crear invitación
- `GET /api/invitations/{id}/` - Detalle de invitación
- `POST /api/invitations/{id}/accept/` - Aceptar invitación
- `POST /api/invitations/{id}/reject/` - Rechazar invitación

### Actividades (`/api/activities/`)
- `GET /api/activities/` - Lista de actividades
- `POST /api/activities/` - Crear actividad
- `GET /api/activities/{id}/` - Detalle de actividad
- `PUT /api/activities/{id}/` - Actualizar actividad
- `DELETE /api/activities/{id}/` - Eliminar actividad

### Dashboard (`/api/dashboard/`)
- `GET /api/dashboard/metrics/` - Métricas del dashboard
- `GET /api/dashboard/charts/` - Datos de gráficos
- `GET /api/dashboard/activities/` - Actividades recientes

### Reportes (`/api/reports/`)
- `GET /api/reports/` - Lista de reportes
- `POST /api/reports/` - Crear reporte
- `GET /api/reports/{id}/` - Detalle de reporte
- `POST /api/reports/{id}/generate/` - Generar reporte

### Alertas (`/api/alerts/`)
- `GET /api/alerts/` - Lista de alertas
- `POST /api/alerts/` - Crear alerta
- `GET /api/alerts/{id}/` - Detalle de alerta
- `PUT /api/alerts/{id}/` - Actualizar alerta
- `DELETE /api/alerts/{id}/` - Eliminar alerta

### Contratos (`/api/contracts/`)
- `GET /api/contracts/` - Lista de contratos
- `POST /api/contracts/` - Crear contrato
- `GET /api/contracts/{id}/` - Detalle de contrato
- `PUT /api/contracts/{id}/` - Actualizar contrato
- `DELETE /api/contracts/{id}/` - Eliminar contrato

### Documentación (`/api/`)
- `GET /api/schema/` - Esquema OpenAPI
- `GET /api/docs/` - Documentación Swagger UI
- `GET /api/redoc/` - Documentación ReDoc

## Configuración de Desarrollo

### Requisitos Previos
- Python 3.8+
- pip (gestor de paquetes de Python)

### Instalación Rápida

1. **Clonar el repositorio**:
   ```bash
   git clone [URL_DEL_REPOSITORIO]
   cd URBANY
   ```

2. **Crear entorno virtual**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Aplicar migraciones**:
   ```bash
   python manage.py migrate
   ```

5. **Crear superusuario** (opcional):
   ```bash
   python manage.py createsuperuser
   ```

6. **Iniciar servidor de desarrollo**:
   ```bash
   python manage.py runserver
   ```

7. **Acceder a la documentación**:
   - Swagger UI: http://localhost:8000/api/docs/
   - ReDoc: http://localhost:8000/api/redoc/

### Testing

#### Ejecutar todas las pruebas:
```bash
python manage.py test
```

#### Ejecutar pruebas por aplicación:
```bash
python manage.py test authentication
python manage.py test users
python manage.py test roles
```

#### Tabla de Testing 'usuarios'
La tabla `usuarios` está disponible para pruebas del sistema de login:
- **Usuario de prueba**: `testuser`
- **Contraseña**: `testpass123`
- **Fecha de creación**: Automática

## Próximos Desarrollos Planificados

## Licencia

MIT

© 2021-2025 CRM URBANY. Todos los derechos reservados.

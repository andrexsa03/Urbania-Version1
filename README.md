# CRM URBANY

## Descripción del Proyecto

CRM URBANY es un sistema de gestión de relaciones con clientes diseñado específicamente para inmobiliarias. Permite gestionar propiedades, contactos, comunicaciones y automatizar procesos de venta inmobiliaria, mejorando la eficiencia operativa y la experiencia del cliente.

## Objetivos

- Centralizar la gestión de propiedades inmobiliarias
- Automatizar procesos de comunicación con clientes
- Integrar con plataformas de marketing y redes sociales
- Facilitar la colaboración entre agentes inmobiliarios
- Proporcionar análisis de datos para la toma de decisiones

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

## Estructura de Directorios

```
Urbania-Version1/
├── docs/                  # Documentación del proyecto
├── src/                   # Código fuente
│   ├── modulo1/           # Módulo de Autenticación y Gestión de Usuarios
│   ├── modulo2/           # Módulo de Gestión de Propiedades
│   ├── modulo3/           # Módulo de Comunicación y Marketing
│   └── modulo4/           # Módulo de Redes Inmobiliarias y Colaboración
├── static/                # Recursos estáticos (CSS, JS, imágenes)
├── tests/                 # Pruebas unitarias e integración
├── requirements.txt       # Dependencias del proyecto
└── README.md              # Documentación principal
```

## Guía de Instalación y Despliegue

### Requisitos Previos
- Python 3.8+
- PostgreSQL 12+
- Redis (para tareas asíncronas)
- Node.js y npm (para componentes frontend)

### Instalación

1. Clonar el repositorio:
   ```
   git clone https://github.com/usuario/Urbania-Version1.git
   cd Urbania-Version1
   ```

2. Crear y activar entorno virtual:
   ```
   python -m venv venv
   
   # En Windows
   venv\Scripts\activate
   
   # En macOS/Linux
   source venv/bin/activate
   ```

3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:
   - Crear archivo `.env` en la raíz del proyecto
   - Definir variables necesarias (ver `.env.example`)

5. Aplicar migraciones:
   ```
   python manage.py migrate
   ```

6. Cargar datos iniciales:
   ```
   python manage.py loaddata initial_data
   ```

7. Iniciar servidor de desarrollo:
   ```
   python manage.py runserver
   ```

### Despliegue en Producción

1. Configurar servidor web (Nginx/Apache)
2. Configurar Gunicorn/uWSGI como servidor WSGI
3. Configurar Celery para tareas asíncronas
4. Configurar base de datos PostgreSQL
5. Configurar Redis para caché y colas
6. Configurar certificados SSL

### Mantenimiento

- Actualizar dependencias regularmente
- Realizar copias de seguridad de la base de datos
- Monitorear logs y rendimiento
- Aplicar actualizaciones de seguridad

## Licencia

MIT

© 2021-2025 CRM URBANY. Todos los derechos reservados.

# Proyecto Django - URBANY

## Descripción
Proyecto Django con arquitectura modular diseñado para aplicaciones web escalables con soporte para APIs REST, comunicación en tiempo real y procesamiento de datos geográficos.

## Requisitos del Sistema

### Software Requerido
- **Python**: 3.8 o superior
- **PostgreSQL**: 12+ con extensión PostGIS instalada
- **Redis**: Servidor configurado y en ejecución
- **Git**: Para control de versiones

### Extensiones de Base de Datos
- PostGIS (extensión geográfica para PostgreSQL)

## Estructura del Proyecto

```
URBANY/
├── core/                   # Configuración principal del proyecto
│   ├── __init__.py
│   ├── settings.py        # Configuraciones del proyecto
│   ├── urls.py           # Rutas principales
│   ├── asgi.py           # Configuración ASGI para Channels
│   └── wsgi.py           # Configuración WSGI
├── apps/                  # Directorio para aplicaciones específicas
│   └── __init__.py
├── manage.py             # Utilidad de línea de comandos de Django
├── requirements.txt      # Dependencias del proyecto
├── .gitignore           # Archivos excluidos del control de versiones
└── README.md            # Este archivo
```

## Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone <url-del-repositorio>
cd URBANY
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de Datos PostgreSQL
DB_NAME=urbany_db
DB_USER=postgres
DB_PASSWORD=tu-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

### 5. Configurar Base de Datos

#### Crear Base de Datos PostgreSQL
```sql
CREATE DATABASE urbany_db;
CREATE USER postgres WITH PASSWORD 'tu-password';
GRANT ALL PRIVILEGES ON DATABASE urbany_db TO postgres;

-- Habilitar PostGIS
\c urbany_db;
CREATE EXTENSION postgis;
```

#### Ejecutar Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Crear Superusuario
```bash
python manage.py createsuperuser
```

### 7. Ejecutar el Servidor de Desarrollo
```bash
python manage.py runserver
```

## Tecnologías Incluidas

### Framework Principal
- **Django 4.2+**: Framework web principal
- **Django REST Framework**: Para APIs REST

### Base de Datos
- **PostgreSQL**: Base de datos principal
- **PostGIS**: Extensión para datos geográficos

### Procesamiento Asíncrono
- **Celery**: Cola de tareas asíncronas
- **Redis**: Broker de mensajes y caché

### Comunicación en Tiempo Real
- **Django Channels**: WebSockets y comunicación asíncrona

### Utilidades
- **Pillow**: Procesamiento de imágenes
- **python-decouple**: Gestión de variables de entorno
- **django-cors-headers**: Manejo de CORS

## Comandos Útiles

### Desarrollo
```bash
# Ejecutar servidor de desarrollo
python manage.py runserver

# Crear nueva aplicación
python manage.py startapp nombre_app

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recopilar archivos estáticos
python manage.py collectstatic
```

### Celery (Tareas Asíncronas)
```bash
# Ejecutar worker de Celery
celery -A core worker --loglevel=info

# Ejecutar Celery Beat (tareas programadas)
celery -A core beat --loglevel=info
```

## Configuración de Producción

### Variables de Entorno para Producción
```env
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
SECRET_KEY=clave-secreta-muy-segura
```

### Servicios Requeridos
1. **PostgreSQL** con PostGIS habilitado
2. **Redis** para Celery y Channels
3. **Servidor Web** (Nginx recomendado)
4. **WSGI/ASGI Server** (Gunicorn + Uvicorn recomendado)

## Estructura de Aplicaciones

Cada nueva funcionalidad debe crearse como una aplicación separada en el directorio `apps/`:

```bash
cd apps
python ../manage.py startapp nombre_aplicacion
```

Luego agregar la aplicación a `INSTALLED_APPS` en `settings.py`:
```python
INSTALLED_APPS = [
    # ... otras apps
    'apps.nombre_aplicacion',
]
```

## Contribución

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## Licencia

Este proyecto está bajo la licencia [MIT](LICENSE).

## Soporte

Para soporte técnico o preguntas sobre el proyecto, contactar al equipo de desarrollo.
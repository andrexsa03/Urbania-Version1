# Aplicación de Usuarios (Users)

## Propósito
La aplicación `users` gestiona toda la información y operaciones relacionadas con los usuarios del sistema URBANY CRM. Proporciona funcionalidades completas de CRUD (Crear, Leer, Actualizar, Eliminar) para usuarios, gestión de perfiles, cambio de contraseñas y estadísticas de usuarios.

## Funciones Principales

### 1. Gestión de Usuarios
- **Endpoints**: CRUD completo para usuarios
- **Propósito**: Administrar información de usuarios del sistema
- **Funcionalidad**: Crear, listar, actualizar y eliminar usuarios

### 2. Gestión de Perfiles
- **Endpoint**: `/api/users/profile/`
- **Propósito**: Manejar información adicional del perfil de usuario
- **Funcionalidad**: Actualizar datos de perfil como biografía, teléfono, dirección

### 3. Cambio de Contraseñas
- **Endpoint**: `POST /api/users/{id}/change-password/`
- **Propósito**: Permitir cambio seguro de contraseñas
- **Funcionalidad**: Validar contraseña actual y establecer nueva

### 4. Asignación de Roles
- **Endpoint**: `POST /api/users/{id}/assign-role/`
- **Propósito**: Gestionar roles de usuarios
- **Funcionalidad**: Asignar y remover roles a usuarios específicos

### 5. Estadísticas de Usuarios
- **Endpoint**: `GET /api/users/stats/`
- **Propósito**: Proporcionar métricas del sistema de usuarios
- **Funcionalidad**: Estadísticas de usuarios activos, registros recientes, etc.

## Archivos y Componentes

### `models.py`
Define los modelos de datos para usuarios:

#### `UserManager`
- **Propósito**: Manager personalizado para el modelo User
- **Métodos**:
  - `create_user(email, password, **extra_fields)`: Crea usuario regular
  - `create_superuser(email, password, **extra_fields)`: Crea superusuario
- **Características**: Usa email como identificador único en lugar de username

#### `User`
- **Hereda de**: `AbstractUser`
- **Campos principales**:
  - `email` (EmailField): Email único del usuario
  - `first_name` (CharField): Nombre del usuario
  - `last_name` (CharField): Apellido del usuario
  - `is_active` (BooleanField): Estado activo del usuario
  - `date_joined` (DateTimeField): Fecha de registro
- **Manager**: `UserManager` personalizado
- **USERNAME_FIELD**: `email`

#### `UserProfile`
- **Relación**: OneToOne con User
- **Campos**:
  - `user` (OneToOneField): Relación con User
  - `bio` (TextField): Biografía del usuario
  - `phone` (CharField): Número de teléfono
  - `address` (TextField): Dirección del usuario
  - `birth_date` (DateField): Fecha de nacimiento
  - `avatar` (ImageField): Imagen de perfil
- **Métodos**:
  - `__str__()`: Representación string del perfil

### `views.py`
Contiene las vistas para manejar operaciones de usuarios:

#### `UserViewSet`
- **Clase**: `ModelViewSet`
- **Modelo**: `User`
- **Permisos**: `IsAuthenticated`
- **Funcionalidades**:
  - CRUD completo para usuarios
  - Filtrado y búsqueda
  - Paginación automática
- **Acciones personalizadas**:
  - `me`: Obtener datos del usuario actual
  - `change_password`: Cambiar contraseña
  - `assign_role`: Asignar rol a usuario

#### `UserProfileViewSet`
- **Clase**: `ModelViewSet`
- **Modelo**: `UserProfile`
- **Permisos**: `IsAuthenticated`
- **Funcionalidades**:
  - Gestión completa de perfiles
  - Actualización de información personal

#### `UserStatsView`
- **Clase**: `APIView`
- **Método**: `GET`
- **Propósito**: Proporcionar estadísticas de usuarios
- **Parámetros**: Ninguno
- **Respuesta**: Métricas del sistema de usuarios

### `serializers.py`
Define los serializadores para validación y serialización:

#### `UserSerializer`
- **Propósito**: Serialización básica de usuarios
- **Campos**:
  - `id`, `email`, `first_name`, `last_name`
  - `is_active`, `date_joined`
- **Validaciones**: Email único, formato válido

#### `UserDetailSerializer`
- **Propósito**: Serialización detallada de usuarios
- **Hereda de**: `UserSerializer`
- **Campos adicionales**:
  - `profile`: Datos del perfil anidados
  - `roles`: Roles asignados al usuario

#### `UserCreateSerializer`
- **Propósito**: Creación de nuevos usuarios
- **Campos**:
  - Todos los campos de User
  - `password`: Campo write-only
- **Validaciones**: Fortaleza de contraseña, unicidad de email

#### `UserProfileSerializer`
- **Propósito**: Serialización de perfiles de usuario
- **Campos**:
  - `bio`, `phone`, `address`, `birth_date`, `avatar`
- **Validaciones**: Formato de teléfono, fechas válidas

#### `PasswordChangeSerializer`
- **Propósito**: Cambio de contraseñas
- **Campos**:
  - `old_password`: Contraseña actual
  - `new_password`: Nueva contraseña
  - `new_password_confirm`: Confirmación de nueva contraseña
- **Validaciones**: Contraseña actual correcta, coincidencia de nuevas contraseñas

### `urls.py`
Define las rutas URL para los endpoints de usuarios:
- `users/` → UserViewSet (CRUD completo)
- `profile/` → UserProfileViewSet
- `stats/` → UserStatsView
- Rutas automáticas generadas por DefaultRouter

### `apps.py`
Configuración de la aplicación Django:
- **Nombre**: `users`
- **Clase**: `UsersConfig`

### `tests.py`
Suite completa de pruebas unitarias:
- **UserManagementTestCase**: Pruebas para endpoints de gestión de usuarios
- **UserProfileTestCase**: Pruebas para gestión de perfiles
- **UserSerializerTestCase**: Pruebas para serializadores

## Parámetros Requeridos por Endpoint

### Crear Usuario (`POST /api/users/`)
```json
{
  "email": "usuario@ejemplo.com",
  "password": "ContraseñaSegura123!",
  "first_name": "Nombre",
  "last_name": "Apellido"
}
```

### Actualizar Usuario (`PUT/PATCH /api/users/{id}/`)
```json
{
  "first_name": "Nuevo Nombre",
  "last_name": "Nuevo Apellido",
  "is_active": true
}
```

### Cambiar Contraseña (`POST /api/users/{id}/change-password/`)
```json
{
  "old_password": "ContraseñaActual",
  "new_password": "NuevaContraseña123!",
  "new_password_confirm": "NuevaContraseña123!"
}
```

### Asignar Rol (`POST /api/users/{id}/assign-role/`)
```json
{
  "role_id": 1,
  "action": "assign"  // o "remove"
}
```

### Actualizar Perfil (`PUT/PATCH /api/users/profile/`)
```json
{
  "bio": "Descripción del usuario",
  "phone": "+1234567890",
  "address": "Dirección completa",
  "birth_date": "1990-01-01"
}
```

## Dependencias

### Internas
- `roles.models`: Para gestión de roles de usuario
- `authentication`: Para autenticación de usuarios

### Externas
- `Django REST Framework`: Framework para API REST
- `Django`: Framework web base
- `Pillow`: Para manejo de imágenes de perfil

## Configuración de Seguridad

### Permisos
- **IsAuthenticated**: Requerido para todas las operaciones
- **IsOwnerOrAdmin**: Para operaciones sensibles como cambio de contraseña
- **IsAdminUser**: Para operaciones administrativas

### Validaciones
- **Email**: Formato válido y unicidad en el sistema
- **Contraseña**: Mínimo 8 caracteres, complejidad requerida
- **Teléfono**: Formato internacional válido
- **Fechas**: Validación de rangos y formatos

## Uso Típico

### Flujo de Creación de Usuario
1. Admin envía datos a `/api/users/`
2. Sistema valida datos y crea usuario
3. Se crea perfil automáticamente
4. Usuario recibe notificación de cuenta creada

### Flujo de Actualización de Perfil
1. Usuario autenticado accede a `/api/users/profile/`
2. Actualiza información personal
3. Sistema valida y guarda cambios
4. Respuesta con datos actualizados

### Flujo de Cambio de Contraseña
1. Usuario envía contraseñas a `/api/users/{id}/change-password/`
2. Sistema valida contraseña actual
3. Valida nueva contraseña
4. Actualiza contraseña con hash seguro

## Notas de Desarrollo

### Testing
- Ejecutar pruebas: `python manage.py test users`
- Cobertura completa de modelos, vistas y serializadores
- Pruebas de permisos y validaciones

### Extensibilidad
- Fácil agregar campos adicionales al perfil
- Soporte para múltiples tipos de usuarios
- Integración con sistemas de notificaciones

### Performance
- Índices en campos de búsqueda frecuente
- Paginación automática en listados
- Optimización de consultas con select_related

### Monitoreo
- Logging de operaciones críticas
- Métricas de uso disponibles
- Auditoría de cambios de usuario
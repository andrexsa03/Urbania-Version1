# Aplicación de Roles (Roles)

## Propósito
La aplicación `roles` implementa un sistema completo de gestión de roles y permisos para el URBANY CRM. Permite definir roles personalizados, asignar permisos específicos y gestionar la asignación de roles a usuarios, proporcionando un control de acceso granular y flexible.

## Funciones Principales

### 1. Gestión de Roles
- **Endpoints**: CRUD completo para roles
- **Propósito**: Crear y administrar roles del sistema
- **Funcionalidad**: Definir roles con nombres, descripciones y permisos asociados

### 2. Gestión de Permisos
- **Endpoints**: CRUD para permisos
- **Propósito**: Definir permisos específicos del sistema
- **Funcionalidad**: Crear permisos con nombres y códigos únicos

### 3. Asignación de Roles a Usuarios
- **Endpoint**: `/api/roles/user-role-management/`
- **Propósito**: Gestionar la relación entre usuarios y roles
- **Funcionalidad**: Asignar, remover y consultar roles de usuarios

### 4. Gestión de Permisos de Roles
- **Endpoints**: `add-permission/`, `remove-permission/`
- **Propósito**: Configurar permisos específicos para cada rol
- **Funcionalidad**: Agregar y quitar permisos de roles existentes

### 5. Estadísticas y Reportes
- **Endpoint**: `GET /api/roles/stats/`
- **Propósito**: Proporcionar métricas del sistema de roles
- **Funcionalidad**: Estadísticas de roles, usuarios asignados, historial

## Archivos y Componentes

### `models.py`
Define los modelos de datos para el sistema de roles:

#### `Permission`
- **Propósito**: Representa permisos específicos del sistema
- **Campos**:
  - `name` (CharField): Nombre descriptivo del permiso
  - `codename` (CharField): Código único del permiso
  - `created_at` (DateTimeField): Fecha de creación
- **Métodos**:
  - `__str__()`: Retorna el nombre del permiso
- **Validaciones**: Codename único en el sistema

#### `Role`
- **Propósito**: Representa roles que pueden ser asignados a usuarios
- **Campos**:
  - `name` (CharField): Nombre único del rol
  - `description` (TextField): Descripción del rol
  - `permissions` (ManyToManyField): Permisos asociados al rol
  - `created_at` (DateTimeField): Fecha de creación
  - `updated_at` (DateTimeField): Fecha de última actualización
- **Métodos**:
  - `__str__()`: Retorna el nombre del rol
  - `has_permission(permission_codename)`: Verifica si el rol tiene un permiso específico
- **Validaciones**: Nombre único del rol

#### `UserRole`
- **Propósito**: Tabla intermedia para la relación Usuario-Rol
- **Campos**:
  - `user` (ForeignKey): Referencia al usuario
  - `role` (ForeignKey): Referencia al rol
  - `assigned_at` (DateTimeField): Fecha de asignación
  - `assigned_by` (ForeignKey): Usuario que realizó la asignación
- **Meta**: Unique constraint en (user, role)
- **Métodos**:
  - `__str__()`: Representación de la asignación

### `views.py`
Contiene las vistas para manejar operaciones de roles:

#### `RoleViewSet`
- **Clase**: `ModelViewSet`
- **Modelo**: `Role`
- **Permisos**: `IsAuthenticated`
- **Funcionalidades**:
  - CRUD completo para roles
  - Filtrado y búsqueda por nombre
  - Paginación automática
- **Acciones personalizadas**:
  - `add_permission`: Agregar permiso a rol
  - `remove_permission`: Quitar permiso de rol
  - `assigned_users`: Listar usuarios con el rol

#### `PermissionViewSet`
- **Clase**: `ModelViewSet`
- **Modelo**: `Permission`
- **Permisos**: `IsAuthenticated`
- **Funcionalidades**:
  - CRUD completo para permisos
  - Validación de codenames únicos

#### `UserRoleManagementView`
- **Clase**: `APIView`
- **Métodos**: `POST`, `DELETE`
- **Propósito**: Gestionar asignaciones de roles a usuarios
- **Funcionalidades**:
  - Asignar roles a usuarios
  - Remover roles de usuarios
  - Validación de permisos

#### `RoleStatsView`
- **Clase**: `APIView`
- **Método**: `GET`
- **Propósito**: Proporcionar estadísticas del sistema de roles
- **Respuesta**: Métricas de roles y asignaciones

#### `UserRoleHistoryView`
- **Clase**: `APIView`
- **Método**: `GET`
- **Propósito**: Mostrar historial de asignaciones de roles
- **Parámetros**: `user_id` (opcional)

### `serializers.py`
Define los serializadores para validación y serialización:

#### `PermissionSerializer`
- **Propósito**: Serialización de permisos
- **Campos**:
  - `id`, `name`, `codename`, `created_at`
- **Validaciones**: Codename único y formato válido

#### `RoleSerializer`
- **Propósito**: Serialización básica de roles
- **Campos**:
  - `id`, `name`, `description`, `created_at`, `updated_at`
- **Validaciones**: Nombre único del rol

#### `RoleDetailSerializer`
- **Propósito**: Serialización detallada de roles
- **Hereda de**: `RoleSerializer`
- **Campos adicionales**:
  - `permissions`: Lista de permisos asociados
  - `user_count`: Número de usuarios con el rol

#### `UserRoleSerializer`
- **Propósito**: Serialización de asignaciones usuario-rol
- **Campos**:
  - `user`, `role`, `assigned_at`, `assigned_by`
- **Validaciones**: Unicidad de asignación

### `urls.py`
Define las rutas URL para los endpoints de roles:
- `roles/` → RoleViewSet (CRUD completo)
- `permissions/` → PermissionViewSet
- `user-role-management/` → UserRoleManagementView
- `stats/` → RoleStatsView
- `user-role-history/` → UserRoleHistoryView

### `apps.py`
Configuración de la aplicación Django:
- **Nombre**: `roles`
- **Clase**: `RolesConfig`

### `tests.py`
Suite completa de pruebas unitarias:
- **RoleManagementTestCase**: Pruebas para gestión de roles
- **PermissionManagementTestCase**: Pruebas para gestión de permisos
- **UserRoleManagementTestCase**: Pruebas para asignación de roles
- **RoleModelTestCase**: Pruebas para métodos de modelos

## Parámetros Requeridos por Endpoint

### Crear Rol (`POST /api/roles/roles/`)
```json
{
  "name": "Nombre del Rol",
  "description": "Descripción detallada del rol"
}
```

### Crear Permiso (`POST /api/roles/permissions/`)
```json
{
  "name": "Nombre del Permiso",
  "codename": "codigo_unico_permiso"
}
```

### Agregar Permiso a Rol (`POST /api/roles/roles/{id}/add-permission/`)
```json
{
  "permission_id": 1
}
```

### Asignar Rol a Usuario (`POST /api/roles/user-role-management/`)
```json
{
  "user_id": 1,
  "role_id": 2
}
```

### Remover Rol de Usuario (`DELETE /api/roles/user-role-management/`)
```json
{
  "user_id": 1,
  "role_id": 2
}
```

## Métodos de Modelo Extendidos

### User Model Extensions
La aplicación extiende el modelo User con métodos adicionales:

#### `has_role(role_name)`
- **Propósito**: Verificar si el usuario tiene un rol específico
- **Parámetros**: `role_name` (string)
- **Retorna**: Boolean
- **Ejemplo**: `user.has_role('admin')`

#### `has_permission(permission_codename)`
- **Propósito**: Verificar si el usuario tiene un permiso específico
- **Parámetros**: `permission_codename` (string)
- **Retorna**: Boolean
- **Ejemplo**: `user.has_permission('view_users')`

#### `get_all_permissions()`
- **Propósito**: Obtener todos los permisos del usuario
- **Retorna**: QuerySet de permisos
- **Ejemplo**: `user.get_all_permissions()`

## Dependencias

### Internas
- `users.models.User`: Modelo de usuario para asignaciones
- `django.contrib.auth`: Sistema de autenticación base

### Externas
- `Django REST Framework`: Framework para API REST
- `Django`: Framework web base

## Configuración de Seguridad

### Permisos de Vista
- **IsAuthenticated**: Requerido para todas las operaciones
- **IsAdminUser**: Para operaciones administrativas sensibles
- **Custom Permissions**: Basados en roles para operaciones específicas

### Validaciones
- **Nombres de Rol**: Únicos en el sistema
- **Codenames de Permiso**: Únicos y formato válido
- **Asignaciones**: Prevención de duplicados usuario-rol

## Casos de Uso Típicos

### Configuración Inicial del Sistema
1. Crear permisos básicos del sistema
2. Definir roles estándar (admin, user, manager)
3. Asignar permisos a roles
4. Asignar roles a usuarios iniciales

### Gestión Diaria de Roles
1. Crear nuevos roles según necesidades
2. Modificar permisos de roles existentes
3. Asignar/remover roles de usuarios
4. Consultar estadísticas de uso

### Auditoría y Monitoreo
1. Revisar historial de asignaciones
2. Generar reportes de roles activos
3. Verificar permisos de usuarios específicos
4. Monitorear cambios en el sistema de roles

## Notas de Desarrollo

### Testing
- Ejecutar pruebas: `python manage.py test roles`
- Cobertura completa de modelos, vistas y serializadores
- Pruebas de integridad de datos y permisos

### Extensibilidad
- Fácil agregar nuevos tipos de permisos
- Soporte para jerarquías de roles
- Integración con sistemas de auditoría

### Performance
- Índices en campos de búsqueda frecuente
- Optimización de consultas con prefetch_related
- Cache de permisos para usuarios activos

### Monitoreo
- Logging de cambios de roles y permisos
- Métricas de uso del sistema de roles
- Alertas para cambios críticos de permisos

## Mejores Prácticas

### Nomenclatura de Permisos
- Usar formato: `accion_recurso` (ej: `view_users`, `edit_reports`)
- Mantener consistencia en nombres
- Documentar propósito de cada permiso

### Gestión de Roles
- Crear roles específicos por función
- Evitar roles con demasiados permisos
- Revisar periódicamente asignaciones

### Seguridad
- Principio de menor privilegio
- Auditoría regular de permisos
- Rotación de roles sensibles
# Aplicación de Autenticación (Authentication)

## Propósito
La aplicación `authentication` maneja todos los aspectos relacionados con la autenticación de usuarios en el sistema URBANY CRM. Proporciona endpoints seguros para registro, inicio de sesión, recuperación de contraseñas y autenticación de dos factores.

## Funciones Principales

### 1. Registro de Usuarios
- **Endpoint**: `POST /api/auth/register/`
- **Propósito**: Registrar nuevos usuarios en el sistema
- **Funcionalidad**: Crea nuevos usuarios, valida datos de entrada y envía emails de verificación

### 2. Inicio de Sesión
- **Endpoint**: `POST /api/auth/login/`
- **Propósito**: Autenticar usuarios existentes
- **Funcionalidad**: Valida credenciales y genera tokens JWT para acceso

### 3. Recuperación de Contraseñas
- **Endpoint**: `POST /api/auth/password-recovery/`
- **Propósito**: Permitir a los usuarios recuperar sus contraseñas
- **Funcionalidad**: Envía emails con enlaces de recuperación

### 4. Autenticación de Dos Factores (2FA)
- **Endpoint**: `POST /api/auth/two-factor-auth/`
- **Propósito**: Proporcionar una capa adicional de seguridad
- **Funcionalidad**: Valida códigos de verificación de dos factores

### 5. Verificación de Estado
- **Endpoint**: `GET /api/auth/health-check/`
- **Propósito**: Verificar el estado del servicio de autenticación
- **Funcionalidad**: Retorna el estado de salud del sistema

## Archivos y Componentes

### `views.py`
Contiene las vistas basadas en clases para manejar las operaciones de autenticación:

#### `RegisterView`
- **Clase**: `APIView`
- **Método**: `POST`
- **Parámetros requeridos**:
  - `email` (string): Email del usuario
  - `password` (string): Contraseña del usuario
  - `first_name` (string): Nombre del usuario
  - `last_name` (string): Apellido del usuario
- **Respuesta**: Datos del usuario creado y mensaje de confirmación

#### `LoginView`
- **Clase**: `APIView`
- **Método**: `POST`
- **Parámetros requeridos**:
  - `email` (string): Email del usuario
  - `password` (string): Contraseña del usuario
- **Respuesta**: Tokens JWT (access y refresh) y datos del usuario

#### `PasswordRecoveryView`
- **Clase**: `APIView`
- **Método**: `POST`
- **Parámetros requeridos**:
  - `email` (string): Email del usuario para recuperación
- **Respuesta**: Mensaje de confirmación de envío de email

#### `TwoFactorAuthView`
- **Clase**: `APIView`
- **Método**: `POST`
- **Parámetros requeridos**:
  - `email` (string): Email del usuario
  - `code` (string): Código de verificación 2FA
- **Respuesta**: Confirmación de autenticación exitosa

#### `HealthCheckView`
- **Clase**: `APIView`
- **Método**: `GET`
- **Parámetros**: Ninguno
- **Respuesta**: Estado de salud del sistema

### `serializers.py`
Define los serializadores para validación y serialización de datos:

#### `LoginSerializer`
- **Propósito**: Validar datos de inicio de sesión
- **Campos**:
  - `email`: EmailField (requerido)
  - `password`: CharField (requerido)
- **Validación**: Verifica credenciales contra la base de datos

#### `RegisterSerializer`
- **Propósito**: Validar datos de registro de usuario
- **Campos**:
  - `email`: EmailField (requerido, único)
  - `password`: CharField (requerido, validación de fortaleza)
  - `first_name`: CharField (requerido)
  - `last_name`: CharField (requerido)
- **Validación**: Verifica unicidad de email y fortaleza de contraseña

### `urls.py`
Define las rutas URL para los endpoints de autenticación:
- `register/` → RegisterView
- `login/` → LoginView
- `password-recovery/` → PasswordRecoveryView
- `two-factor-auth/` → TwoFactorAuthView
- `health-check/` → HealthCheckView

### `apps.py`
Configuración de la aplicación Django:
- **Nombre**: `authentication`
- **Clase**: `AuthenticationConfig`

### `tests.py`
Suite completa de pruebas unitarias:
- **AuthenticationTestCase**: Pruebas para endpoints de API
- **AuthSerializerTestCase**: Pruebas para serializadores

## Dependencias

### Internas
- `users.models.User`: Modelo de usuario personalizado
- `rest_framework_simplejwt`: Para manejo de tokens JWT

### Externas
- `Django REST Framework`: Framework para API REST
- `Django`: Framework web base

## Configuración de Seguridad

### Tokens JWT
- **Access Token**: Duración corta para operaciones autenticadas
- **Refresh Token**: Duración larga para renovar access tokens

### Validaciones
- **Email**: Formato válido y unicidad
- **Contraseña**: Mínimo 8 caracteres, debe incluir mayúsculas, minúsculas y números
- **Rate Limiting**: Protección contra ataques de fuerza bruta

## Uso Típico

### Flujo de Registro
1. Cliente envía datos de registro a `/api/auth/register/`
2. Sistema valida datos y crea usuario
3. Se envía email de verificación
4. Usuario recibe confirmación de registro

### Flujo de Login
1. Cliente envía credenciales a `/api/auth/login/`
2. Sistema valida credenciales
3. Se generan tokens JWT
4. Cliente recibe tokens para futuras peticiones autenticadas

### Flujo de Recuperación
1. Cliente solicita recuperación en `/api/auth/password-recovery/`
2. Sistema envía email con enlace de recuperación
3. Usuario sigue enlace para restablecer contraseña

## Notas de Desarrollo

### Testing
- Ejecutar pruebas: `python manage.py test authentication`
- Cobertura completa de endpoints y serializadores
- Pruebas de casos exitosos y de error

### Extensibilidad
- Fácil agregar nuevos métodos de autenticación
- Soporte para proveedores OAuth (preparado para futuras implementaciones)
- Integración con sistemas de notificaciones

### Monitoreo
- Endpoint de health check para monitoreo de sistema
- Logging de intentos de autenticación
- Métricas de uso disponibles
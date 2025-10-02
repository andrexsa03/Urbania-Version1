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

1. **Módulo 1: Autenticación y Gestión de Usuarios**
   - Equipo: Backend 1
   - Funcionalidades: Login, registro, recuperación de contraseña, perfiles de usuario

2. **Módulo 2: Gestión de Propiedades**
   - Equipo: Backend 2
   - Funcionalidades: Creación, edición y publicación de propiedades inmobiliarias

3. **Módulo 3: Comunicación y Marketing**
   - Equipo: Backend 3
   - Funcionalidades: Email marketing, plantillas, integraciones con redes sociales

4. **Módulo 4: Redes Inmobiliarias y Colaboración**
   - Equipo: Backend 4
   - Funcionalidades: Creación de redes, invitaciones, compartición de propiedades

## Historias de Usuario

### Desarrollo (Backend)
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

### Maquetación (Frontend)
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

## Guía de Configuración Inicial

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
   - Crear archivo `.env` basado en `.env.example`
   - Configurar credenciales de base de datos y servicios externos

5. Ejecutar migraciones:
   ```
   python manage.py migrate
   ```

6. Iniciar servidor de desarrollo:
   ```
   python manage.py runserver
   ```

## Licencia

© 2021-2025 CRM URBANY. Todos los derechos reservados.
# Módulo 4: Redes Inmobiliarias y Colaboración

## Descripción
Este módulo gestiona la creación de redes inmobiliarias, invitaciones y compartición de propiedades entre agentes.

## Funcionalidades Implementadas
- Gestión de redes inmobiliarias (HU26)

## Funcionalidades Pendientes
- Gestión de invitaciones (HU08)
- Integración con redes inmobiliarias externas (HU07)

## Dependencias Técnicas
- Django 4.2+
- Django Channels para comunicación en tiempo real
- PostgreSQL para almacenamiento de datos
- WebSockets para notificaciones en tiempo real

## Dependencias del Módulo
- **Módulo 1 (Autenticación y Gestión de Usuarios)**:
  - Utilizado para la gestión de permisos de usuarios en redes colaborativas
  - Integración para autenticación de usuarios en invitaciones
- **Módulo 2 (Gestión de Propiedades)**:
  - Utilizado para compartir y gestionar propiedades entre agentes
  - Integración para asignación de propiedades a redes inmobiliarias

## Estructura Base del Módulo
```
modulo4/
├── networks/              # Gestión de redes inmobiliarias
│   ├── models.py          # Modelos de redes y membresías
│   ├── views.py           # Vistas para gestión de redes
│   └── permissions.py     # Permisos específicos de redes
├── invitations/           # Sistema de invitaciones
│   ├── models.py          # Modelos de invitaciones
│   ├── services.py        # Servicios de envío de invitaciones
│   └── tasks.py           # Tareas programadas
├── sharing/               # Compartición de propiedades
│   ├── models.py          # Modelos de compartición
│   └── views.py           # Vistas para compartir propiedades
└── api/                   # Endpoints de API
    ├── urls.py            # Rutas de API
    └── views.py           # Vistas de API
```

### Componentes Principales
- **networks/**: Gestiona la creación y administración de redes inmobiliarias
- **invitations/**: Maneja el sistema de invitaciones a redes
- **sharing/**: Implementa la compartición de propiedades entre agentes
- **api/**: Define los endpoints de API para el módulo

### Implementación de Nuevas Funcionalidades
Para implementar una nueva funcionalidad en este módulo:

1. **Definir modelos**: Crear o extender modelos en el directorio correspondiente
2. **Implementar lógica de negocio**: Desarrollar servicios en archivos `services.py`
3. **Configurar permisos**: Definir permisos específicos en `permissions.py`
4. **Actualizar API**: Añadir nuevos endpoints en `api/views.py`

Ejemplo de implementación de una nueva funcionalidad de compartición:
```python
# En sharing/models.py
class PropertySharing(models.Model):
    property = models.ForeignKey('modulo2.Property', on_delete=models.CASCADE)
    network = models.ForeignKey('networks.Network', on_delete=models.CASCADE)
    shared_by = models.ForeignKey('modulo1.User', on_delete=models.CASCADE)
    permissions = models.CharField(max_length=50, choices=PERMISSION_CHOICES)
    
# En sharing/services.py
def share_property_with_network(property_id, network_id, user_id, permissions):
    # Lógica para compartir propiedad con una red
    sharing = PropertySharing.objects.create(
        property_id=property_id,
        network_id=network_id,
        shared_by_id=user_id,
        permissions=permissions
    )
    notify_network_members(network_id, property_id)
    return sharing
```

## Equipo Responsable
Backend 4
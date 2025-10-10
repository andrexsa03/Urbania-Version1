# MÓDULO 4: REDES INMOBILIARIAS Y COLABORACIÓN

## Descripción General

El Módulo 4 del sistema URBANY implementa funcionalidades avanzadas para la gestión de redes inmobiliarias y colaboración entre agentes. Este módulo incluye dos componentes principales:

1. **HU24 - Panel de Contratos**: Sistema completo de gestión de contratos inmobiliarios
2. **HU25 - Mensajería Interna**: Sistema de comunicación en tiempo real entre usuarios

## Arquitectura del Módulo

### Aplicaciones Implementadas

```
URBANY/
├── contracts/          # HU24 - Gestión de Contratos
├── messaging/          # HU25 - Mensajería Interna
├── networks/           # Gestión de redes inmobiliarias
├── invitations/        # Sistema de invitaciones
├── sharing/            # Compartir recursos
├── activities/         # Registro de actividades
├── navigation/         # Navegación del sistema
├── dashboard/          # Panel de control
├── reports/            # Reportes y estadísticas
└── alerts/             # Sistema de alertas
```

## HU24 - PANEL DE CONTRATOS

### Descripción
Sistema completo para la gestión de contratos inmobiliarios que permite crear, editar, visualizar y gestionar contratos con diferentes estados y tipos.

### Modelos de Datos

#### Contract
Modelo principal que representa un contrato inmobiliario.

**Campos principales:**
- `contract_number`: Número único del contrato
- `title`: Título descriptivo
- `contract_type`: Tipo (Sale, Rent, Lease, Management)
- `status`: Estado (Draft, Active, Signed, Completed, Cancelled, Expired)
- `priority`: Prioridad (Low, Medium, High, Urgent)
- `client_name`: Nombre del cliente
- `agent`: Agente responsable
- `property_address`: Dirección de la propiedad
- `contract_value`: Valor del contrato
- `commission_rate`: Tasa de comisión
- `commission_amount`: Monto de comisión
- `start_date`: Fecha de inicio
- `end_date`: Fecha de finalización
- `signed_date`: Fecha de firma
- `terms_and_conditions`: Términos y condiciones
- `contract_file`: Archivo del contrato
- `attachments`: Archivos adjuntos

#### ContractPayment
Modelo para gestionar pagos relacionados con contratos.

**Campos principales:**
- `contract`: Relación con Contract
- `payment_type`: Tipo de pago
- `amount`: Monto
- `due_date`: Fecha de vencimiento
- `paid_date`: Fecha de pago
- `status`: Estado del pago

#### ContractDocument
Modelo para documentos asociados a contratos.

**Campos principales:**
- `contract`: Relación con Contract
- `document_type`: Tipo de documento
- `title`: Título del documento
- `file`: Archivo
- `uploaded_by`: Usuario que subió el archivo

#### ContractNote
Modelo para notas y comentarios en contratos.

**Campos principales:**
- `contract`: Relación con Contract
- `note_type`: Tipo de nota
- `content`: Contenido de la nota
- `created_by`: Usuario que creó la nota

### API Endpoints

#### Contratos
- `GET /api/contratos/` - Listar contratos
- `POST /api/contratos/` - Crear contrato
- `GET /api/contratos/{id}/` - Obtener contrato específico
- `PUT /api/contratos/{id}/` - Actualizar contrato
- `DELETE /api/contratos/{id}/` - Eliminar contrato

#### Pagos
- `GET /api/contratos/{id}/payments/` - Listar pagos del contrato
- `POST /api/contratos/{id}/payments/` - Crear pago

#### Documentos
- `GET /api/contratos/{id}/documents/` - Listar documentos del contrato
- `POST /api/contratos/{id}/documents/` - Subir documento

#### Notas
- `GET /api/contratos/{id}/notes/` - Listar notas del contrato
- `POST /api/contratos/{id}/notes/` - Crear nota

#### Estadísticas y Utilidades
- `GET /api/contratos/stats/` - Estadísticas de contratos
- `POST /api/contratos/update-status/` - Actualizar estado de contrato
- `POST /api/contratos/bulk-actions/` - Acciones en lote
- `GET /api/contratos/search/` - Búsqueda avanzada
- `GET /api/contratos/my-contracts/` - Contratos del usuario actual
- `GET /api/contratos/expiring/` - Contratos próximos a vencer
- `GET /api/contratos/summary-by-agent/` - Resumen por agente

#### Datos de Prueba
- `POST /api/contratos/generate-mock/` - Generar contratos de prueba
- `DELETE /api/contratos/clear-user-contracts/` - Limpiar contratos del usuario

### Serializers

#### ContractListSerializer
Serializer para la lista de contratos con información resumida.

#### ContractDetailSerializer
Serializer detallado que incluye pagos, documentos y notas.

#### ContractCreateUpdateSerializer
Serializer para crear y actualizar contratos con validaciones.

#### ContractStatsSerializer
Serializer para estadísticas de contratos.

### Funcionalidades Implementadas

1. **Gestión Completa de Contratos**
   - CRUD completo de contratos
   - Diferentes tipos y estados
   - Sistema de prioridades
   - Cálculo automático de comisiones

2. **Gestión de Pagos**
   - Seguimiento de pagos programados
   - Estados de pago
   - Recordatorios de vencimiento

3. **Gestión de Documentos**
   - Subida de archivos
   - Categorización de documentos
   - Control de versiones

4. **Sistema de Notas**
   - Comentarios y seguimiento
   - Diferentes tipos de notas
   - Historial de actividades

5. **Búsqueda y Filtros**
   - Búsqueda por múltiples campos
   - Filtros por estado, tipo, fecha
   - Ordenamiento personalizable

6. **Estadísticas y Reportes**
   - Métricas de rendimiento
   - Análisis por agente
   - Reportes de comisiones

### Datos de Prueba
Se han generado 25 contratos de prueba con:
- 8 contratos de venta
- 2 contratos de renta
- 9 contratos de arrendamiento
- 6 contratos de administración

## HU25 - MENSAJERÍA INTERNA

### Descripción
Sistema de mensajería interna que permite la comunicación en tiempo real entre usuarios del sistema, con soporte para conversaciones directas, grupales y de soporte.

### Modelos de Datos

#### Conversation
Modelo principal para representar conversaciones.

**Campos principales:**
- `title`: Título de la conversación
- `conversation_type`: Tipo (direct, group, support, announcement)
- `participants`: Participantes de la conversación
- `created_by`: Usuario que creó la conversación
- `is_active`: Estado de la conversación

#### Message
Modelo para mensajes individuales.

**Campos principales:**
- `conversation`: Conversación a la que pertenece
- `sender`: Usuario que envió el mensaje
- `message_type`: Tipo (text, file, image, system)
- `content`: Contenido del mensaje
- `attachment`: Archivo adjunto
- `is_read`: Estado de lectura
- `reply_to`: Mensaje al que responde
- `read_at`: Fecha de lectura

#### MessageRead
Modelo para rastrear lecturas de mensajes.

**Campos principales:**
- `message`: Mensaje leído
- `user`: Usuario que leyó
- `read_at`: Fecha de lectura

#### MessageReaction
Modelo para reacciones a mensajes.

**Campos principales:**
- `message`: Mensaje
- `user`: Usuario que reaccionó
- `reaction_type`: Tipo de reacción (like, love, laugh, wow, sad, angry)

#### UserStatus
Modelo para estado de conexión de usuarios.

**Campos principales:**
- `user`: Usuario
- `status`: Estado (online, away, busy, offline)
- `last_seen`: Última vez visto
- `custom_message`: Mensaje personalizado

### API Endpoints

#### Conversaciones
- `GET /api/mensajes/conversations/` - Listar conversaciones
- `POST /api/mensajes/conversations/` - Crear conversación
- `GET /api/mensajes/conversations/{id}/` - Obtener conversación específica
- `PUT /api/mensajes/conversations/{id}/` - Actualizar conversación
- `DELETE /api/mensajes/conversations/{id}/` - Eliminar conversación

#### Mensajes
- `GET /api/mensajes/conversations/{id}/messages/` - Listar mensajes de conversación
- `POST /api/mensajes/conversations/{id}/messages/` - Enviar mensaje
- `GET /api/mensajes/messages/{id}/` - Obtener mensaje específico
- `PUT /api/mensajes/messages/{id}/` - Actualizar mensaje
- `DELETE /api/mensajes/messages/{id}/` - Eliminar mensaje

#### Reacciones
- `POST /api/mensajes/messages/{id}/reactions/` - Agregar reacción
- `DELETE /api/mensajes/messages/{id}/reactions/remove/` - Eliminar reacción

#### Búsqueda y Estadísticas
- `GET /api/mensajes/search/` - Buscar mensajes
- `GET /api/mensajes/stats/` - Estadísticas de mensajería

#### Acciones en Lote
- `POST /api/mensajes/bulk-actions/` - Acciones en lote sobre mensajes

#### Estado de Usuarios
- `GET /api/mensajes/status/` - Obtener estado del usuario
- `POST /api/mensajes/status/` - Actualizar estado del usuario
- `GET /api/mensajes/online-users/` - Usuarios en línea

#### Datos de Prueba
- `POST /api/mensajes/generate-mock/` - Generar mensajes de prueba
- `DELETE /api/mensajes/clear-user-data/` - Limpiar datos del usuario

### Serializers

#### ConversationListSerializer
Serializer para lista de conversaciones con información resumida.

#### ConversationDetailSerializer
Serializer detallado que incluye todos los mensajes.

#### MessageSerializer
Serializer para mensajes con información completa.

#### MessageCreateSerializer
Serializer para crear mensajes con validaciones.

#### UserStatusSerializer
Serializer para estado de usuarios.

### Funcionalidades Implementadas

1. **Conversaciones Múltiples**
   - Conversaciones directas (1:1)
   - Conversaciones grupales
   - Soporte técnico
   - Anuncios

2. **Mensajería Rica**
   - Mensajes de texto
   - Archivos adjuntos
   - Imágenes
   - Mensajes de sistema
   - Respuestas a mensajes

3. **Sistema de Reacciones**
   - 6 tipos de reacciones (👍❤️😂😮😢😠)
   - Una reacción por usuario por mensaje

4. **Estado de Lectura**
   - Seguimiento de mensajes leídos
   - Marcado automático al abrir conversación
   - Contadores de mensajes no leídos

5. **Estado de Usuarios**
   - Estados: online, away, busy, offline
   - Última vez visto
   - Mensajes personalizados de estado

6. **Búsqueda Avanzada**
   - Búsqueda por contenido
   - Filtros por conversación y tipo
   - Paginación de resultados

7. **Acciones en Lote**
   - Marcar como leído/no leído
   - Eliminar múltiples mensajes

### Datos de Prueba
Se han generado:
- 15 conversaciones de prueba
- 159 mensajes realistas
- 4 conversaciones directas
- 3 conversaciones grupales
- 4 conversaciones de soporte
- 4 anuncios

## Configuración del Proyecto

### Settings.py
```python
INSTALLED_APPS = [
    # ... otras apps
    'contracts',
    'messaging',
    # ... resto de apps del módulo 4
]
```

### URLs.py
```python
urlpatterns = [
    # ... otras URLs
    path('api/contratos/', include('contracts.urls')),
    path('api/mensajes/', include('messaging.urls')),
    # ... resto de URLs
]
```

### Base de Datos
Las migraciones han sido aplicadas correctamente para ambas aplicaciones:
- `contracts.0001_initial`
- `messaging.0001_initial`

## Comandos de Gestión

### Contratos
```bash
# Generar contratos de prueba
python manage.py create_mock_contracts --count 25

# Limpiar contratos de un usuario
python manage.py clear_user_contracts --user-email admin@urbany.com
```

### Mensajería
```bash
# Generar conversaciones y mensajes de prueba
python manage.py create_mock_messages --conversations 15 --messages-per-conversation 12

# Generar para un usuario específico
python manage.py create_mock_messages --user-email admin@urbany.com
```

## Panel de Administración

Ambas aplicaciones están completamente configuradas en el panel de administración de Django con:

### Contracts Admin
- Vista de lista con filtros por tipo, estado, prioridad
- Campos de búsqueda por cliente, agente, dirección
- Fieldsets organizados por categorías
- Campos de solo lectura para metadatos
- Enlaces a objetos relacionados

### Messaging Admin
- Vista de lista de conversaciones y mensajes
- Filtros por tipo de conversación y estado
- Búsqueda por participantes y contenido
- Información detallada de archivos adjuntos
- Estados de usuario con indicadores visuales

## Seguridad y Permisos

### Autenticación
- Todos los endpoints requieren autenticación
- Uso de JWT tokens para autenticación

### Autorización
- Los usuarios solo pueden acceder a sus propios contratos
- Los mensajes están limitados a conversaciones donde el usuario participa
- Funciones administrativas restringidas al personal

### Validaciones
- Validación de datos en serializers
- Verificación de permisos en vistas
- Sanitización de archivos subidos

## Rendimiento y Optimización

### Consultas Optimizadas
- Uso de `select_related` y `prefetch_related`
- Paginación en todas las listas
- Índices en campos de búsqueda frecuente

### Caching
- Preparado para implementar cache en consultas frecuentes
- Optimización de consultas de estadísticas

## Testing

### Estructura de Tests
```
contracts/tests.py
messaging/tests.py
```

### Cobertura
- Tests unitarios para modelos
- Tests de integración para APIs
- Tests de permisos y seguridad

## Próximas Mejoras

### Django Channels (Pendiente)
- WebSockets para mensajería en tiempo real
- Notificaciones push
- Estado de conexión en tiempo real

### Funcionalidades Adicionales
- Notificaciones por email
- Integración con calendario
- Exportación de reportes
- API de webhooks

## Conclusión

El Módulo 4 proporciona una base sólida para la gestión de contratos inmobiliarios y comunicación interna. Las funcionalidades implementadas cubren los casos de uso principales y están preparadas para escalar según las necesidades del negocio.

La arquitectura modular permite agregar nuevas funcionalidades fácilmente, y la documentación completa facilita el mantenimiento y desarrollo futuro del sistema.
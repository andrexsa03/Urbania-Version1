# Módulo 2: Gestión de Propiedades

## Descripción
Este módulo maneja la creación, edición y publicación de propiedades inmobiliarias en el sistema CRM URBANY.

## Funcionalidades Implementadas
- Gestión de propiedades inmobiliarias (HU14)
- Categorización y etiquetado de propiedades

## Funcionalidades Pendientes
- Integración con portales inmobiliarios
- Sistema de búsqueda avanzada de propiedades

## Dependencias Técnicas
- Django 4.2+
- Django REST Framework
- PostgreSQL (con extensión PostGIS para geolocalización)
- Pillow para manejo de imágenes

## Dependencias del Módulo
- **Módulo 1 (Autenticación y Gestión de Usuarios)**:
  - Utilizado para la asignación de propiedades a usuarios específicos
  - Integración con el sistema de permisos para control de acceso a propiedades
- **Módulo 3 (Comunicación y Marketing)**:
  - Utilizado para la promoción y publicación de propiedades
  - Integración para notificaciones sobre cambios en propiedades

## Estructura Base del Módulo
```
modulo2/
├── properties/            # Gestión de propiedades
│   ├── models.py          # Modelos de propiedades y características
│   ├── views.py           # Vistas para gestión de propiedades
│   └── serializers.py     # Serializadores para datos de propiedades
├── media/                 # Gestión de archivos multimedia
│   ├── models.py          # Modelos para imágenes y documentos
│   └── services.py        # Servicios de procesamiento de imágenes
├── search/                # Sistema de búsqueda
│   ├── indexing.py        # Indexación de propiedades
│   └── views.py           # Vistas para búsqueda
└── api/                   # Endpoints de API
    ├── urls.py            # Rutas de API
    └── views.py           # Vistas de API
```

### Componentes Principales
- **properties/**: Gestiona los datos básicos de las propiedades inmobiliarias
- **media/**: Maneja imágenes, documentos y otros archivos relacionados con propiedades
- **search/**: Implementa el sistema de búsqueda y filtrado de propiedades
- **api/**: Define los endpoints de API para el módulo

### Implementación de Nuevas Funcionalidades
Para implementar una nueva funcionalidad en este módulo:

1. **Extender modelos**: Añadir nuevos campos o modelos relacionados en `properties/models.py`
2. **Implementar servicios**: Crear servicios específicos en archivos `services.py`
3. **Actualizar API**: Añadir nuevos endpoints en `api/views.py` y rutas en `api/urls.py`
4. **Implementar pruebas**: Añadir pruebas unitarias y de integración

Ejemplo de implementación de una nueva característica de propiedad:
```python
# En properties/models.py
class PropertyFeature(models.Model):
    property = models.ForeignKey('Property', on_delete=models.CASCADE)
    feature_type = models.CharField(max_length=50)
    value = models.CharField(max_length=100)
    
# En properties/serializers.py
class PropertyFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyFeature
        fields = ['id', 'feature_type', 'value']
```

## Equipo Responsable
Backend 2
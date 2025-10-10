from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role, Permission, UserRole

User = get_user_model()


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Permission model.
    """
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_codename(self, value):
        """Validate that codename is unique and follows naming convention."""
        if not value.replace('_', '').isalnum():
            raise serializers.ValidationError(
                "El código debe contener solo letras, números y guiones bajos."
            )
        
        # Check uniqueness
        if self.instance:
            # Update case - exclude current instance
            if Permission.objects.exclude(id=self.instance.id).filter(codename=value).exists():
                raise serializers.ValidationError(
                    "Ya existe un permiso con este código."
                )
        else:
            # Create case
            if Permission.objects.filter(codename=value).exists():
                raise serializers.ValidationError(
                    "Ya existe un permiso con este código."
                )
        
        return value


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model with permissions.
    """
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="Lista de IDs de permisos a asignar al rol"
    )
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'is_active', 'created_at', 'updated_at',
            'permissions', 'permission_ids', 'users_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'users_count']

    def get_users_count(self, obj):
        """Get the number of users with this role."""
        return obj.users.count()

    def validate_name(self, value):
        """Validate that role name is unique."""
        if self.instance:
            # Update case - exclude current instance
            if Role.objects.exclude(id=self.instance.id).filter(name=value).exists():
                raise serializers.ValidationError(
                    "Ya existe un rol con este nombre."
                )
        else:
            # Create case
            if Role.objects.filter(name=value).exists():
                raise serializers.ValidationError(
                    "Ya existe un rol con este nombre."
                )
        
        return value

    def create(self, validated_data):
        """Create role with permissions."""
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        
        return role

    def update(self, instance, validated_data):
        """Update role with permissions."""
        permission_ids = validated_data.pop('permission_ids', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update permissions if provided
        if permission_ids is not None:
            permissions = Permission.objects.filter(id__in=permission_ids)
            instance.permissions.set(permissions)
        
        return instance


class RoleListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for role listing.
    """
    permissions_count = serializers.SerializerMethodField()
    users_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'description', 'is_active', 
            'permissions_count', 'users_count', 'created_at'
        ]

    def get_permissions_count(self, obj):
        """Get the number of permissions for this role."""
        return obj.permissions.count()

    def get_users_count(self, obj):
        """Get the number of users with this role."""
        return obj.users.count()


class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for UserRole model.
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id', 'user', 'role', 'assigned_at', 'assigned_by',
            'user_email', 'user_full_name', 'role_name'
        ]
        read_only_fields = ['id', 'assigned_at', 'assigned_by']

    def create(self, validated_data):
        """Create user role assignment."""
        # Set assigned_by from request context
        request = self.context.get('request')
        if request and request.user:
            validated_data['assigned_by'] = request.user
        
        return super().create(validated_data)


class RoleAssignmentSerializer(serializers.Serializer):
    """
    Serializer for role assignment operations.
    """
    role_id = serializers.IntegerField(help_text="ID del rol a asignar")
    action = serializers.ChoiceField(
        choices=['assign', 'remove'],
        default='assign',
        help_text="Acción a realizar: 'assign' para asignar, 'remove' para quitar"
    )

    def validate_role_id(self, value):
        """Validate that role exists and is active."""
        try:
            role = Role.objects.get(id=value)
            if not role.is_active:
                raise serializers.ValidationError(
                    "No se puede asignar un rol inactivo."
                )
            return value
        except Role.DoesNotExist:
            raise serializers.ValidationError(
                "El rol especificado no existe."
            )

    def save(self, **kwargs):
        """Perform role assignment or removal."""
        user = kwargs.get('user')
        role_id = self.validated_data['role_id']
        action = self.validated_data['action']
        request = self.context.get('request')
        
        role = Role.objects.get(id=role_id)
        
        if action == 'assign':
            # Check if user already has this role
            if user.has_role(role.name):
                return {
                    'message': f'El usuario ya tiene el rol {role.name}',
                    'role': role.name,
                    'action': 'already_assigned'
                }
            
            # Assign role
            user.add_role(role.name, assigned_by=request.user if request else None)
            return {
                'message': f'Rol {role.name} asignado exitosamente',
                'role': role.name,
                'action': 'assigned'
            }
        
        elif action == 'remove':
            # Check if user has this role
            if not user.has_role(role.name):
                return {
                    'message': f'El usuario no tiene el rol {role.name}',
                    'role': role.name,
                    'action': 'not_assigned'
                }
            
            # Remove role
            user.remove_role(role.name)
            return {
                'message': f'Rol {role.name} removido exitosamente',
                'role': role.name,
                'action': 'removed'
            }


class UserWithRolesSerializer(serializers.ModelSerializer):
    """
    Serializer for User with their roles.
    """
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 'is_active',
            'date_joined', 'roles', 'permissions'
        ]

    def get_roles(self, obj):
        """Get user roles."""
        user_roles = UserRole.objects.filter(user=obj).select_related('role')
        return [{
            'id': ur.role.id,
            'name': ur.role.name,
            'description': ur.role.description,
            'assigned_at': ur.assigned_at,
            'assigned_by': ur.assigned_by.email if ur.assigned_by else None
        } for ur in user_roles]

    def get_permissions(self, obj):
        """Get user permissions through roles."""
        permissions = obj.get_all_permissions()
        return [{
            'id': perm.id,
            'name': perm.name,
            'codename': perm.codename,
            'description': perm.description
        } for perm in permissions]


class PermissionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating permissions.
    """
    class Meta:
        model = Permission
        fields = ['name', 'codename', 'description']

    def validate_codename(self, value):
        """Validate codename format and uniqueness."""
        if not value.replace('_', '').isalnum():
            raise serializers.ValidationError(
                "El código debe contener solo letras, números y guiones bajos."
            )
        
        if Permission.objects.filter(codename=value).exists():
            raise serializers.ValidationError(
                "Ya existe un permiso con este código."
            )
        
        return value


class RolePermissionManagementSerializer(serializers.Serializer):
    """
    Serializer for managing permissions within a role.
    """
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs de permisos"
    )
    action = serializers.ChoiceField(
        choices=['add', 'remove', 'set'],
        help_text="Acción: 'add' agregar, 'remove' quitar, 'set' establecer (reemplazar todos)"
    )

    def validate_permission_ids(self, value):
        """Validate that all permission IDs exist."""
        existing_ids = set(Permission.objects.filter(id__in=value).values_list('id', flat=True))
        provided_ids = set(value)
        
        if existing_ids != provided_ids:
            missing_ids = provided_ids - existing_ids
            raise serializers.ValidationError(
                f"Los siguientes IDs de permisos no existen: {list(missing_ids)}"
            )
        
        return value

    def save(self, **kwargs):
        """Perform permission management on role."""
        role = kwargs.get('role')
        permission_ids = self.validated_data['permission_ids']
        action = self.validated_data['action']
        
        permissions = Permission.objects.filter(id__in=permission_ids)
        
        if action == 'add':
            role.permissions.add(*permissions)
            message = f"Se agregaron {len(permissions)} permisos al rol {role.name}"
        elif action == 'remove':
            role.permissions.remove(*permissions)
            message = f"Se removieron {len(permissions)} permisos del rol {role.name}"
        elif action == 'set':
            role.permissions.set(permissions)
            message = f"Se establecieron {len(permissions)} permisos para el rol {role.name}"
        
        return {
            'message': message,
            'role': role.name,
            'action': action,
            'permissions_count': role.permissions.count()
        }
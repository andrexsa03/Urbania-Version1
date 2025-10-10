from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from phonenumber_field.serializerfields import PhoneNumberField
from .models import UserProfile, Inmobiliaria

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    """
    age = serializers.ReadOnlyField()
    phone_number = PhoneNumberField(required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = (
            'phone_number', 'date_of_birth', 'gender', 'address',
            'city', 'country', 'postal_code', 'avatar', 'bio',
            'website', 'is_public', 'age', 'created_at', 'updated_at'
        )
        read_only_fields = ('age', 'created_at', 'updated_at')

    def validate_website(self, value):
        """Validate website URL format."""
        if value and not value.startswith(('http://', 'https://')):
            value = f'https://{value}'
        return value


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for User model including profile information.
    """
    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'is_active', 'is_staff', 'is_superuser', 'is_email_verified',
            'date_joined', 'last_login', 'created_at', 'updated_at',
            'profile', 'roles', 'permissions'
        )
        read_only_fields = (
            'id', 'date_joined', 'last_login', 'created_at', 'updated_at',
            'is_email_verified'
        )

    def get_roles(self, obj):
        """Get user roles."""
        return [role.name for role in obj.get_roles()]

    def get_permissions(self, obj):
        """Get user permissions."""
        return [perm.codename for perm in obj.get_permissions()]


class UserListSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for User model in list views.
    """
    full_name = serializers.ReadOnlyField()
    roles_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'is_active', 'is_staff', 'date_joined', 'roles_count'
        )

    def get_roles_count(self, obj):
        """Get count of user roles."""
        return obj.get_roles().count()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users.
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='La contraseña debe tener al menos 8 caracteres.'
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text='Confirme su contraseña.'
    )

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'password',
            'password_confirm', 'is_active', 'is_staff'
        )
        extra_kwargs = {
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'El email es requerido.',
                    'invalid': 'Ingrese un email válido.',
                    'unique': 'Ya existe un usuario con este email.'
                }
            },
            'first_name': {
                'required': True,
                'error_messages': {
                    'required': 'El nombre es requerido.'
                }
            },
            'last_name': {
                'required': True,
                'error_messages': {
                    'required': 'El apellido es requerido.'
                }
            }
        }

    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Ya existe un usuario con este email.'
            )
        return value

    def validate_password(self, value):
        """Validate password using Django's password validators."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Validate password confirmation."""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')

        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': 'Las contraseñas no coinciden.'
            })

        return attrs

    def create(self, validated_data):
        """Create a new user with the validated data."""
        # Remove password_confirm from validated_data
        validated_data.pop('password_confirm', None)
        
        # Create user
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing users.
    """
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'is_active', 'is_staff'
        )
        extra_kwargs = {
            'first_name': {
                'required': False
            },
            'last_name': {
                'required': False
            }
        }


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.
    """
    phone_number = PhoneNumberField(required=False, allow_blank=True)

    class Meta:
        model = UserProfile
        fields = (
            'phone_number', 'date_of_birth', 'gender', 'address',
            'city', 'country', 'postal_code', 'avatar', 'bio',
            'website', 'is_public'
        )

    def validate_website(self, value):
        """Validate website URL format."""
        if value and not value.startswith(('http://', 'https://')):
            value = f'https://{value}'
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for changing user password.
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Contraseña actual.'
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Nueva contraseña.'
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text='Confirme la nueva contraseña.'
    )

    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'La contraseña actual es incorrecta.'
            )
        return value

    def validate_new_password(self, value):
        """Validate new password using Django's password validators."""
        try:
            validate_password(value, user=self.context['request'].user)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Validate password confirmation."""
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')

        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'Las contraseñas no coinciden.'
            })

        return attrs

    def save(self):
        """Change user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class UserRoleAssignmentSerializer(serializers.Serializer):
    """
    Serializer for assigning/removing roles to/from users.
    """
    role_id = serializers.IntegerField(required=True)
    action = serializers.ChoiceField(
        choices=['assign', 'remove'],
        required=True,
        help_text='Acción a realizar: assign (asignar) o remove (remover)'
    )

    def validate_role_id(self, value):
        """Validate that the role exists."""
        from roles.models import Role
        try:
            role = Role.objects.get(id=value, is_active=True)
            return role
        except Role.DoesNotExist:
            raise serializers.ValidationError(
                'El rol especificado no existe o está inactivo.'
            )

    def save(self, user):
        """Assign or remove role from user."""
        role = self.validated_data['role_id']
        action = self.validated_data['action']
        assigned_by = self.context['request'].user

        if action == 'assign':
            user_role = user.add_role(role, assigned_by=assigned_by)
            return {
                'message': f'Rol "{role.name}" asignado exitosamente.',
                'role': role.name,
                'action': 'assigned'
            }
        elif action == 'remove':
            success = user.remove_role(role)
            if success:
                return {
                    'message': f'Rol "{role.name}" removido exitosamente.',
                    'role': role.name,
                    'action': 'removed'
                }
            else:
                raise serializers.ValidationError(
                    f'El usuario no tiene el rol "{role.name}" asignado.'
                )


class InmobiliariaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Inmobiliaria.
    """
    direccion_completa = serializers.ReadOnlyField()
    telefono = PhoneNumberField(required=True)

    class Meta:
        model = Inmobiliaria
        fields = (
            'id', 'nombre', 'email', 'telefono', 'direccion', 'ciudad',
            'pais', 'codigo_postal', 'sitio_web', 'descripcion', 'logo',
            'is_active', 'fecha_registro', 'fecha_actualizacion',
            'direccion_completa'
        )
        read_only_fields = ('id', 'fecha_registro', 'fecha_actualizacion')
        extra_kwargs = {
            'nombre': {
                'required': True,
                'error_messages': {
                    'required': 'El nombre de la inmobiliaria es requerido.',
                    'blank': 'El nombre no puede estar vacío.'
                }
            },
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'El email es requerido.',
                    'invalid': 'Ingrese un email válido.',
                    'unique': 'Ya existe una inmobiliaria con este email.'
                }
            },
            'telefono': {
                'required': True,
                'error_messages': {
                    'required': 'El teléfono es requerido.',
                    'invalid': 'Ingrese un número de teléfono válido.'
                }
            }
        }

    def validate_email(self, value):
        """
        Validar formato de email.
        """
        if not value:
            raise serializers.ValidationError('El email es requerido.')
        return value.lower()

    def validate_sitio_web(self, value):
        """
        Validar y normalizar URL del sitio web.
        """
        if value and not value.startswith(('http://', 'https://')):
            value = f'https://{value}'
        return value


class InmobiliariaCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear una nueva inmobiliaria.
    """
    telefono = PhoneNumberField(required=True)

    class Meta:
        model = Inmobiliaria
        fields = (
            'nombre', 'email', 'telefono', 'direccion', 'ciudad',
            'pais', 'codigo_postal', 'sitio_web', 'descripcion', 'logo'
        )
        extra_kwargs = {
            'nombre': {
                'required': True,
                'error_messages': {
                    'required': 'El nombre de la inmobiliaria es requerido.',
                    'blank': 'El nombre no puede estar vacío.'
                }
            },
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'El email es requerido.',
                    'invalid': 'Ingrese un email válido.',
                    'unique': 'Ya existe una inmobiliaria con este email.'
                }
            },
            'telefono': {
                'required': True,
                'error_messages': {
                    'required': 'El teléfono es requerido.',
                    'invalid': 'Ingrese un número de teléfono válido.'
                }
            }
        }

    def validate_email(self, value):
        """
        Validar formato de email y unicidad.
        """
        if not value:
            raise serializers.ValidationError('El email es requerido.')
        
        # Verificar unicidad
        if Inmobiliaria.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('Ya existe una inmobiliaria con este email.')
        
        return value.lower()

    def validate_sitio_web(self, value):
        """
        Validar y normalizar URL del sitio web.
        """
        if value and not value.startswith(('http://', 'https://')):
            value = f'https://{value}'
        return value

    def create(self, validated_data):
        """
        Crear una nueva inmobiliaria.
        """
        inmobiliaria = Inmobiliaria.objects.create(**validated_data)
        return inmobiliaria


class UserPortalProfileSerializer(serializers.ModelSerializer):
    """
    Serializer para el perfil público del usuario en portales inmobiliarios.
    """
    full_name = serializers.ReadOnlyField()
    phone_number = PhoneNumberField(source='profile.phone_number', required=False)
    avatar = serializers.ImageField(source='profile.avatar', required=False)
    bio = serializers.CharField(source='profile.bio', required=False, max_length=500)
    website = serializers.URLField(source='profile.website', required=False)

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'avatar', 'bio', 'website'
        )
        read_only_fields = ('id',)
        extra_kwargs = {
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'El email es requerido.',
                    'invalid': 'Ingrese un email válido.'
                }
            },
            'first_name': {
                'required': True,
                'error_messages': {
                    'required': 'El nombre es requerido.'
                }
            },
            'last_name': {
                'required': True,
                'error_messages': {
                    'required': 'El apellido es requerido.'
                }
            }
        }

    def validate_website(self, value):
        """
        Validar y normalizar URL del sitio web.
        """
        if value and not value.startswith(('http://', 'https://')):
            value = f'https://{value}'
        return value

    def update(self, instance, validated_data):
        """
        Actualizar el perfil público del usuario.
        """
        # Extraer datos del perfil
        profile_data = {}
        for field in ['phone_number', 'avatar', 'bio', 'website']:
            if f'profile.{field}' in validated_data:
                profile_data[field] = validated_data.pop(f'profile.{field}')
        
        # Actualizar usuario
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Actualizar perfil si hay datos
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()
        
        return instance
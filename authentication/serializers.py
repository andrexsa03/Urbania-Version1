from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from phonenumber_field.serializerfields import PhoneNumberField

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login with email and password.
    """
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'El email es requerido.',
            'invalid': 'Ingrese un email válido.'
        }
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        error_messages={
            'required': 'La contraseña es requerida.'
        }
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )

            if not user:
                raise serializers.ValidationError(
                    'Credenciales inválidas. Verifique su email y contraseña.',
                    code='authorization'
                )

            if not user.is_active:
                raise serializers.ValidationError(
                    'La cuenta de usuario está desactivada.',
                    code='authorization'
                )

            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Debe incluir email y contraseña.',
                code='authorization'
            )

    def create(self, validated_data):
        """Generate JWT tokens for the authenticated user."""
        user = validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
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
    phone_number = PhoneNumberField(
        required=False,
        allow_blank=True,
        help_text='Número de teléfono en formato internacional.'
    )

    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'password', 
            'password_confirm', 'phone_number'
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
        phone_number = validated_data.pop('phone_number', None)
        
        # Create user
        user = User.objects.create_user(**validated_data)
        
        # Update profile with phone number if provided
        if phone_number:
            user.profile.phone_number = phone_number
            user.profile.save()
        
        return user


class PasswordRecoverySerializer(serializers.Serializer):
    """
    Serializer for password recovery (dummy implementation).
    """
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'El email es requerido.',
            'invalid': 'Ingrese un email válido.'
        }
    )

    def validate_email(self, value):
        """Validate that the email exists in the system."""
        if not User.objects.filter(email=value).exists():
            # For security reasons, we don't reveal if the email exists
            # but we still validate the format
            pass
        return value

    def save(self):
        """Mock email sending for password recovery."""
        email = self.validated_data['email']
        # Here you would normally send an email with a recovery link
        # For now, we just return a success message
        return {
            'message': f'Si el email {email} está registrado, recibirás un enlace de recuperación.',
            'email': email
        }


class TwoFactorAuthSerializer(serializers.Serializer):
    """
    Serializer for two-factor authentication (mock implementation).
    """
    code = serializers.CharField(
        required=True,
        min_length=6,
        max_length=6,
        error_messages={
            'required': 'El código es requerido.',
            'min_length': 'El código debe tener 6 dígitos.',
            'max_length': 'El código debe tener 6 dígitos.'
        }
    )
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'El email es requerido.',
            'invalid': 'Ingrese un email válido.'
        }
    )

    def validate_code(self, value):
        """Validate the 2FA code format."""
        if not value.isdigit():
            raise serializers.ValidationError(
                'El código debe contener solo números.'
            )
        return value

    def validate_email(self, value):
        """Validate that the email exists."""
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                'Usuario no encontrado.'
            )
        return value

    def validate(self, attrs):
        """Mock validation - always accepts the code."""
        # In a real implementation, you would validate the code against
        # a stored value or external service
        code = attrs.get('code')
        email = attrs.get('email')
        
        # Mock validation - always successful
        user = User.objects.get(email=email)
        attrs['user'] = user
        attrs['verified'] = True
        
        return attrs

    def save(self):
        """Return success response for 2FA verification."""
        user = self.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return {
            'message': 'Código 2FA verificado correctamente.',
            'user': user,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'verified': True
        }


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user data in authentication responses.
    """
    full_name = serializers.ReadOnlyField()
    roles = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'is_email_verified', 'is_active', 'date_joined',
            'roles', 'permissions'
        )
        read_only_fields = (
            'id', 'is_email_verified', 'is_active', 'date_joined'
        )

    def get_roles(self, obj):
        """Get user roles."""
        return [role.name for role in obj.get_roles()]

    def get_permissions(self, obj):
        """Get user permissions."""
        return [perm.codename for perm in obj.get_permissions()]
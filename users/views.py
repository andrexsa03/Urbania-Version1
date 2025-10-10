from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from datetime import datetime

from .models import UserProfile, Inmobiliaria
from .serializers import (
    UserDetailSerializer,
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    PasswordChangeSerializer,
    UserRoleAssignmentSerializer,
    InmobiliariaSerializer,
    InmobiliariaCreateSerializer,
    UserPortalProfileSerializer
)

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or admins to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner or admin users
        return obj == request.user or request.user.is_staff


class UserViewSet(ModelViewSet):
    """
    ViewSet for managing users with CRUD operations.
    """
    queryset = User.objects.all().order_by('-date_joined')
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        else:
            return UserDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == 'create':
            permission_classes = [IsAdminUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        operation_description="Get list of users",
        responses={
            200: UserListSerializer(many=True),
            401: "Unauthorized"
        },
        tags=['Users']
    )
    def list(self, request, *args, **kwargs):
        """List all users."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get user details",
        responses={
            200: UserDetailSerializer,
            401: "Unauthorized",
            404: "User not found"
        },
        tags=['Users']
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific user."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new user (Admin only)",
        request_body=UserCreateSerializer,
        responses={
            201: UserDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Admin required"
        },
        tags=['Users']
    )
    def create(self, request, *args, **kwargs):
        """Create a new user (Admin only)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Return detailed user information
        detail_serializer = UserDetailSerializer(user)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Update user information",
        request_body=UserUpdateSerializer,
        responses={
            200: UserDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "User not found"
        },
        tags=['Users']
    )
    def update(self, request, *args, **kwargs):
        """Update user information."""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update user information",
        request_body=UserUpdateSerializer,
        responses={
            200: UserDetailSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "User not found"
        },
        tags=['Users']
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update user information."""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete user (Admin only or self)",
        responses={
            204: "User deleted successfully",
            401: "Unauthorized",
            403: "Forbidden",
            404: "User not found"
        },
        tags=['Users']
    )
    def destroy(self, request, *args, **kwargs):
        """Delete user (Admin only or self)."""
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='get',
        operation_description="Get current user profile",
        responses={
            200: UserDetailSerializer,
            401: "Unauthorized"
        },
        tags=['Users']
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Get current user profile."""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        method='post',
        operation_description="Assign or remove role from user",
        request_body=UserRoleAssignmentSerializer,
        responses={
            200: openapi.Response(
                description="Role assignment successful",
                examples={
                    "application/json": {
                        "message": "Rol asignado exitosamente",
                        "role": "admin",
                        "action": "assigned"
                    }
                }
            ),
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Admin required",
            404: "User not found"
        },
        tags=['Users']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def assign_role(self, request, pk=None):
        """Assign or remove role from user."""
        user = self.get_object()
        serializer = UserRoleAssignmentSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                result = serializer.save(user=user)
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': 'Error al procesar la asignación de rol',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'error': 'Datos inválidos',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    API endpoint for managing user profiles.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get user profile",
        responses={
            200: UserProfileSerializer,
            401: "Unauthorized",
            404: "Profile not found"
        },
        tags=['User Profile']
    )
    def get(self, request, user_id=None):
        """Get user profile."""
        if user_id:
            user = get_object_or_404(User, id=user_id)
            # Check if profile is public or user is owner/admin
            if not user.profile.is_public and user != request.user and not request.user.is_staff:
                return Response({
                    'error': 'Perfil privado'
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            user = request.user
        
        serializer = UserProfileSerializer(user.profile)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="Update user profile",
        request_body=UserProfileUpdateSerializer,
        responses={
            200: UserProfileSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden"
        },
        tags=['User Profile']
    )
    def put(self, request, user_id=None):
        """Update user profile."""
        if user_id:
            user = get_object_or_404(User, id=user_id)
            # Only allow owner or admin to update
            if user != request.user and not request.user.is_staff:
                return Response({
                    'error': 'Sin permisos para actualizar este perfil'
                }, status=status.HTTP_403_FORBIDDEN)
        else:
            user = request.user
        
        serializer = UserProfileUpdateSerializer(
            user.profile,
            data=request.data,
            partial=True
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response({
            'error': 'Datos inválidos',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """
    API endpoint for changing user password.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Change user password",
        request_body=PasswordChangeSerializer,
        responses={
            200: openapi.Response(
                description="Password changed successfully",
                examples={
                    "application/json": {
                        "message": "Contraseña cambiada exitosamente"
                    }
                }
            ),
            400: "Bad Request - Invalid data",
            401: "Unauthorized"
        },
        tags=['Users']
    )
    def post(self, request):
        """Change user password."""
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({
                    'message': 'Contraseña cambiada exitosamente'
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': 'Error al cambiar la contraseña',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'error': 'Datos inválidos',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserStatsView(APIView):
    """
    API endpoint for user statistics (Admin only).
    """
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get user statistics (Admin only)",
        responses={
            200: openapi.Response(
                description="User statistics",
                examples={
                    "application/json": {
                        "total_users": 150,
                        "active_users": 142,
                        "inactive_users": 8,
                        "staff_users": 5,
                        "verified_emails": 130,
                        "recent_registrations": 12
                    }
                }
            ),
            401: "Unauthorized",
            403: "Forbidden - Admin required"
        },
        tags=['Users']
    )
    def get(self, request):
        """Get user statistics."""
        from datetime import datetime, timedelta
        
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        inactive_users = User.objects.filter(is_active=False).count()
        staff_users = User.objects.filter(is_staff=True).count()
        verified_emails = User.objects.filter(is_email_verified=True).count()
        
        # Recent registrations (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_registrations = User.objects.filter(
            date_joined__gte=thirty_days_ago
        ).count()
        
        return Response({
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': inactive_users,
            'staff_users': staff_users,
            'verified_emails': verified_emails,
            'recent_registrations': recent_registrations,
            'statistics_date': datetime.now().isoformat()
        })


class InmobiliariaRegistrationView(APIView):
    """
    Vista para el registro de inmobiliarias en el CRM URBANY.
    """
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="Registrar una nueva inmobiliaria en el CRM URBANY",
        request_body=InmobiliariaCreateSerializer,
        responses={
            201: openapi.Response(
                description="Inmobiliaria registrada exitosamente",
                examples={
                    "application/json": {
                        "message": "Inmobiliaria registrada exitosamente",
                        "inmobiliaria": {
                            "id": 1,
                            "nombre": "Inmobiliaria Ejemplo",
                            "email": "contacto@ejemplo.com",
                            "telefono": "+1234567890"
                        }
                    }
                }
            ),
            400: "Bad Request - Datos inválidos",
            409: "Conflict - Email ya existe"
        },
        tags=['Inmobiliarias']
    )
    def post(self, request):
        """
        Registrar una nueva inmobiliaria.
        """
        serializer = InmobiliariaCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                inmobiliaria = serializer.save()
                response_serializer = InmobiliariaSerializer(inmobiliaria)
                
                return Response({
                    'message': 'Inmobiliaria registrada exitosamente',
                    'inmobiliaria': response_serializer.data
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': 'Error al registrar la inmobiliaria',
                    'details': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'error': 'Datos inválidos',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileUpdateView(APIView):
    """
    Vista para actualizar el perfil del usuario.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Actualizar información del perfil del usuario",
        request_body=UserProfileUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Perfil actualizado exitosamente",
                examples={
                    "application/json": {
                        "message": "Perfil actualizado exitosamente",
                        "profile": {
                            "phone_number": "+1234567890",
                            "bio": "Agente inmobiliario especializado",
                            "website": "https://miwebsite.com"
                        }
                    }
                }
            ),
            400: "Bad Request - Datos inválidos",
            401: "Unauthorized"
        },
        tags=['User Profile']
    )
    def put(self, request):
        """
        Actualizar el perfil del usuario autenticado.
        """
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Perfil no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Perfil actualizado exitosamente',
                'profile': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Datos inválidos',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfilePhotoUploadView(APIView):
    """
    Vista para cargar la imagen de perfil del usuario.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Cargar imagen de perfil del usuario",
        manual_parameters=[
            openapi.Parameter(
                'avatar',
                openapi.IN_FORM,
                description="Imagen de perfil",
                type=openapi.TYPE_FILE,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Imagen cargada exitosamente",
                examples={
                    "application/json": {
                        "message": "Imagen de perfil actualizada exitosamente",
                        "avatar_url": "/media/avatars/user_123.jpg"
                    }
                }
            ),
            400: "Bad Request - Archivo inválido",
            401: "Unauthorized"
        },
        tags=['User Profile']
    )
    def post(self, request):
        """
        Cargar imagen de perfil del usuario.
        """
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            return Response({
                'error': 'Perfil no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        if 'avatar' not in request.FILES:
            return Response({
                'error': 'No se proporcionó ninguna imagen'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        avatar_file = request.FILES['avatar']
        
        # Validar tipo de archivo
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if avatar_file.content_type not in allowed_types:
            return Response({
                'error': 'Tipo de archivo no permitido. Use JPEG, PNG, GIF o WebP'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar tamaño (máximo 5MB)
        if avatar_file.size > 5 * 1024 * 1024:
            return Response({
                'error': 'El archivo es demasiado grande. Máximo 5MB'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        profile.avatar = avatar_file
        profile.save()
        
        return Response({
            'message': 'Imagen de perfil actualizada exitosamente',
            'avatar_url': profile.avatar.url if profile.avatar else None
        }, status=status.HTTP_200_OK)


class UserPortalProfileView(APIView):
    """
    Vista para gestionar el perfil público del usuario en portales inmobiliarios.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Obtener perfil público del usuario para portales",
        responses={
            200: UserPortalProfileSerializer,
            401: "Unauthorized"
        },
        tags=['Portal Profile']
    )
    def get(self, request):
        """
        Obtener el perfil público del usuario.
        """
        try:
            serializer = UserPortalProfileSerializer(request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'Error interno'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        operation_description="Actualizar perfil público del usuario para portales",
        request_body=UserPortalProfileSerializer,
        responses={
            200: openapi.Response(
                description="Perfil público actualizado exitosamente",
                examples={
                    "application/json": {
                        "message": "Perfil público actualizado exitosamente",
                        "profile": {
                            "full_name": "Juan Pérez",
                            "email": "juan@ejemplo.com",
                            "phone_number": "+1234567890"
                        }
                    }
                }
            ),
            400: "Bad Request - Datos inválidos",
            401: "Unauthorized"
        },
        tags=['Portal Profile']
    )
    def put(self, request):
        """
        Actualizar el perfil público del usuario.
        """
        serializer = UserPortalProfileSerializer(request.user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Perfil público actualizado exitosamente',
                'profile': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Datos inválidos',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

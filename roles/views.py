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

from .models import Role, Permission, UserRole
from .serializers import (
    RoleSerializer,
    RoleListSerializer,
    PermissionSerializer,
    PermissionCreateSerializer,
    UserRoleSerializer,
    RoleAssignmentSerializer,
    UserWithRolesSerializer,
    RolePermissionManagementSerializer
)

User = get_user_model()


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit, but allow read access to authenticated users.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_staff


class RoleViewSet(ModelViewSet):
    """
    ViewSet for managing roles with CRUD operations.
    """
    queryset = Role.objects.all().order_by('name')
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return RoleListSerializer
        return RoleSerializer

    @swagger_auto_schema(
        operation_description="Get list of roles",
        responses={
            200: RoleListSerializer(many=True),
            401: "Unauthorized"
        },
        tags=['Roles']
    )
    def list(self, request, *args, **kwargs):
        """List all roles."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get role details",
        responses={
            200: RoleSerializer,
            401: "Unauthorized",
            404: "Role not found"
        },
        tags=['Roles']
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific role."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new role (Admin only)",
        request_body=RoleSerializer,
        responses={
            201: RoleSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Admin required"
        },
        tags=['Roles']
    )
    def create(self, request, *args, **kwargs):
        """Create a new role (Admin only)."""
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update role information (Admin only)",
        request_body=RoleSerializer,
        responses={
            200: RoleSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Admin required",
            404: "Role not found"
        },
        tags=['Roles']
    )
    def update(self, request, *args, **kwargs):
        """Update role information (Admin only)."""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update role information (Admin only)",
        request_body=RoleSerializer,
        responses={
            200: RoleSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Admin required",
            404: "Role not found"
        },
        tags=['Roles']
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update role information (Admin only)."""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete role (Admin only)",
        responses={
            204: "Role deleted successfully",
            401: "Unauthorized",
            403: "Forbidden - Admin required",
            404: "Role not found",
            400: "Bad Request - Role has assigned users"
        },
        tags=['Roles']
    )
    def destroy(self, request, *args, **kwargs):
        """Delete role (Admin only)."""
        role = self.get_object()
        
        # Check if role has assigned users
        if role.users.exists():
            return Response({
                'error': 'No se puede eliminar un rol que tiene usuarios asignados',
                'users_count': role.users.count()
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='post',
        operation_description="Manage permissions for a role (Admin only)",
        request_body=RolePermissionManagementSerializer,
        responses={
            200: openapi.Response(
                description="Permission management successful",
                examples={
                    "application/json": {
                        "message": "Se agregaron 3 permisos al rol admin",
                        "role": "admin",
                        "action": "add",
                        "permissions_count": 15
                    }
                }
            ),
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Admin required",
            404: "Role not found"
        },
        tags=['Roles']
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def manage_permissions(self, request, pk=None):
        """Manage permissions for a role (Admin only)."""
        role = self.get_object()
        serializer = RolePermissionManagementSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            try:
                result = serializer.save(role=role)
                return Response(result, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({
                    'error': 'Error al gestionar permisos',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'error': 'Datos inválidos',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        method='get',
        operation_description="Get users assigned to this role",
        responses={
            200: UserWithRolesSerializer(many=True),
            401: "Unauthorized",
            404: "Role not found"
        },
        tags=['Roles']
    )
    @action(detail=True, methods=['get'])
    def users(self, request, pk=None):
        """Get users assigned to this role."""
        role = self.get_object()
        users = role.users.all().order_by('email')
        serializer = UserWithRolesSerializer(users, many=True)
        return Response(serializer.data)


class PermissionViewSet(ModelViewSet):
    """
    ViewSet for managing permissions with CRUD operations.
    """
    queryset = Permission.objects.all().order_by('name')
    permission_classes = [IsAdminOrReadOnly]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return PermissionCreateSerializer
        return PermissionSerializer

    @swagger_auto_schema(
        operation_description="Get list of permissions",
        responses={
            200: PermissionSerializer(many=True),
            401: "Unauthorized"
        },
        tags=['Permissions']
    )
    def list(self, request, *args, **kwargs):
        """List all permissions."""
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Get permission details",
        responses={
            200: PermissionSerializer,
            401: "Unauthorized",
            404: "Permission not found"
        },
        tags=['Permissions']
    )
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific permission."""
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new permission (Admin only)",
        request_body=PermissionCreateSerializer,
        responses={
            201: PermissionSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Admin required"
        },
        tags=['Permissions']
    )
    def create(self, request, *args, **kwargs):
        """Create a new permission (Admin only)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        permission = serializer.save()
        
        # Return detailed permission information
        detail_serializer = PermissionSerializer(permission)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_description="Update permission information (Admin only)",
        request_body=PermissionSerializer,
        responses={
            200: PermissionSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Admin required",
            404: "Permission not found"
        },
        tags=['Permissions']
    )
    def update(self, request, *args, **kwargs):
        """Update permission information (Admin only)."""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update permission information (Admin only)",
        request_body=PermissionSerializer,
        responses={
            200: PermissionSerializer,
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden - Admin required",
            404: "Permission not found"
        },
        tags=['Permissions']
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update permission information (Admin only)."""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete permission (Admin only)",
        responses={
            204: "Permission deleted successfully",
            401: "Unauthorized",
            403: "Forbidden - Admin required",
            404: "Permission not found",
            400: "Bad Request - Permission is assigned to roles"
        },
        tags=['Permissions']
    )
    def destroy(self, request, *args, **kwargs):
        """Delete permission (Admin only)."""
        permission = self.get_object()
        
        # Check if permission is assigned to any roles
        if permission.roles.exists():
            return Response({
                'error': 'No se puede eliminar un permiso asignado a roles',
                'roles_count': permission.roles.count(),
                'roles': list(permission.roles.values_list('name', flat=True))
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().destroy(request, *args, **kwargs)


class UserRoleManagementView(APIView):
    """
    API endpoint for managing user role assignments.
    """
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Assign or remove role from user (Admin only)",
        request_body=RoleAssignmentSerializer,
        responses={
            200: openapi.Response(
                description="Role assignment successful",
                examples={
                    "application/json": {
                        "message": "Rol admin asignado exitosamente",
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
        tags=['User Roles']
    )
    def post(self, request, user_id):
        """Assign or remove role from user."""
        user = get_object_or_404(User, id=user_id)
        serializer = RoleAssignmentSerializer(
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


class RoleStatsView(APIView):
    """
    API endpoint for role statistics (Admin only).
    """
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Get role statistics (Admin only)",
        responses={
            200: openapi.Response(
                description="Role statistics",
                examples={
                    "application/json": {
                        "total_roles": 5,
                        "active_roles": 4,
                        "inactive_roles": 1,
                        "total_permissions": 25,
                        "total_user_roles": 150,
                        "roles_breakdown": [
                            {"role": "admin", "users_count": 3},
                            {"role": "editor", "users_count": 15},
                            {"role": "viewer", "users_count": 132}
                        ]
                    }
                }
            ),
            401: "Unauthorized",
            403: "Forbidden - Admin required"
        },
        tags=['Roles']
    )
    def get(self, request):
        """Get role statistics."""
        total_roles = Role.objects.count()
        active_roles = Role.objects.filter(is_active=True).count()
        inactive_roles = Role.objects.filter(is_active=False).count()
        total_permissions = Permission.objects.count()
        total_user_roles = UserRole.objects.count()
        
        # Roles breakdown
        roles_breakdown = []
        for role in Role.objects.all():
            roles_breakdown.append({
                'role': role.name,
                'users_count': role.users.count(),
                'permissions_count': role.permissions.count(),
                'is_active': role.is_active
            })
        
        return Response({
            'total_roles': total_roles,
            'active_roles': active_roles,
            'inactive_roles': inactive_roles,
            'total_permissions': total_permissions,
            'total_user_roles': total_user_roles,
            'roles_breakdown': roles_breakdown,
            'statistics_date': timezone.now().isoformat()
        })


class UserRoleHistoryView(APIView):
    """
    API endpoint for viewing user role assignment history.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Get user role assignment history",
        responses={
            200: UserRoleSerializer(many=True),
            401: "Unauthorized",
            403: "Forbidden",
            404: "User not found"
        },
        tags=['User Roles']
    )
    def get(self, request, user_id=None):
        """Get user role assignment history."""
        if user_id:
            # Admin can view any user's history, users can only view their own
            if not request.user.is_staff and request.user.id != int(user_id):
                return Response({
                    'error': 'Sin permisos para ver el historial de este usuario'
                }, status=status.HTTP_403_FORBIDDEN)
            
            user = get_object_or_404(User, id=user_id)
        else:
            user = request.user
        
        user_roles = UserRole.objects.filter(user=user).order_by('-assigned_at')
        serializer = UserRoleSerializer(user_roles, many=True)
        return Response(serializer.data)


# Import timezone for statistics
from django.utils import timezone

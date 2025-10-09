from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    PasswordRecoverySerializer,
    TwoFactorAuthSerializer,
    UserSerializer
)

User = get_user_model()


class LoginView(APIView):
    """
    API endpoint for user login.
    
    Authenticates user credentials and returns JWT tokens.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Authenticate user and return JWT tokens",
        request_body=LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful",
                examples={
                    "application/json": {
                        "message": "Login exitoso",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "full_name": "John Doe"
                        },
                        "tokens": {
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid credentials",
            401: "Unauthorized - Invalid credentials"
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Handle user login."""
        serializer = LoginSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            try:
                auth_data = serializer.save()
                user_serializer = UserSerializer(auth_data['user'])
                
                return Response({
                    'message': 'Login exitoso',
                    'user': user_serializer.data,
                    'tokens': {
                        'refresh': auth_data['refresh'],
                        'access': auth_data['access']
                    }
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': 'Error interno del servidor',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'error': 'Datos inválidos',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    API endpoint for user logout.
    
    Blacklists the refresh token to invalidate the session.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Logout user and blacklist refresh token",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
            },
            required=['refresh']
        ),
        responses={
            200: openapi.Response(
                description="Logout successful",
                examples={
                    "application/json": {
                        "message": "Logout exitoso"
                    }
                }
            ),
            400: "Bad Request - Invalid token"
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Handle user logout."""
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({
                    'error': 'Token de refresh requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({
                'message': 'Logout exitoso'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Token inválido',
                'detail': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(APIView):
    """
    API endpoint for user registration.
    
    Creates a new user account with the provided information.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Register a new user account",
        request_body=RegisterSerializer,
        responses={
            201: openapi.Response(
                description="Registration successful",
                examples={
                    "application/json": {
                        "message": "Usuario registrado exitosamente",
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe",
                            "full_name": "John Doe"
                        },
                        "email_sent": True
                    }
                }
            ),
            400: "Bad Request - Validation errors"
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Handle user registration."""
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = serializer.save()
                user_serializer = UserSerializer(user)
                
                # Mock email confirmation sending
                self._send_confirmation_email(user)
                
                return Response({
                    'message': 'Usuario registrado exitosamente',
                    'user': user_serializer.data,
                    'email_sent': True,
                    'note': 'Se ha enviado un email de confirmación a su dirección de correo.'
                }, status=status.HTTP_201_CREATED)
                
            except Exception as e:
                return Response({
                    'error': 'Error interno del servidor',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'error': 'Datos inválidos',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def _send_confirmation_email(self, user):
        """
        Mock function to simulate sending confirmation email.
        In a real implementation, this would send an actual email.
        """
        # Mock implementation - just log the action
        print(f"Mock: Sending confirmation email to {user.email}")
        return True


class PasswordRecoveryView(APIView):
    """
    API endpoint for password recovery.
    
    Dummy implementation that always returns success.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Request password recovery (dummy implementation)",
        request_body=PasswordRecoverySerializer,
        responses={
            200: openapi.Response(
                description="Recovery email sent (always successful)",
                examples={
                    "application/json": {
                        "message": "Si el email está registrado, recibirás un enlace de recuperación.",
                        "email_sent": True
                    }
                }
            ),
            400: "Bad Request - Invalid email format"
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Handle password recovery request."""
        serializer = PasswordRecoverySerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = serializer.save()
                
                return Response({
                    'message': result['message'],
                    'email_sent': True,
                    'note': 'Esta es una implementación dummy que siempre retorna éxito.'
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': 'Error interno del servidor',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'error': 'Datos inválidos',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class TwoFactorAuthView(APIView):
    """
    API endpoint for two-factor authentication.
    
    Mock implementation that always validates codes as correct.
    """
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        operation_description="Verify 2FA code (mock implementation - always successful)",
        request_body=TwoFactorAuthSerializer,
        responses={
            200: openapi.Response(
                description="2FA verification successful",
                examples={
                    "application/json": {
                        "message": "Código 2FA verificado correctamente",
                        "verified": True,
                        "user": {
                            "id": 1,
                            "email": "user@example.com",
                            "first_name": "John",
                            "last_name": "Doe"
                        },
                        "tokens": {
                            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
                        }
                    }
                }
            ),
            400: "Bad Request - Invalid code format",
            404: "User not found"
        },
        tags=['Authentication']
    )
    def post(self, request):
        """Handle 2FA code verification."""
        serializer = TwoFactorAuthSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                result = serializer.save()
                user_serializer = UserSerializer(result['user'])
                
                return Response({
                    'message': result['message'],
                    'verified': result['verified'],
                    'user': user_serializer.data,
                    'tokens': {
                        'refresh': result['refresh'],
                        'access': result['access']
                    },
                    'note': 'Esta es una implementación mock que siempre valida el código como correcto.'
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'error': 'Error interno del servidor',
                    'detail': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'error': 'Datos inválidos',
            'details': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


# Function-based view alternatives (if preferred)
@swagger_auto_schema(
    method='post',
    operation_description="Health check endpoint for authentication service",
    responses={
        200: openapi.Response(
            description="Service is healthy",
            examples={
                "application/json": {
                    "status": "healthy",
                    "service": "authentication",
                    "version": "1.0.0"
                }
            }
        )
    },
    tags=['Health Check']
)
@api_view(['POST', 'GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for the authentication service.
    """
    return Response({
        'status': 'healthy',
        'service': 'authentication',
        'version': '1.0.0',
        'endpoints': {
            'login': '/auth/login/',
            'register': '/auth/register/',
            'recover': '/auth/recover/',
            '2fa': '/auth/2fa/'
        }
    }, status=status.HTTP_200_OK)

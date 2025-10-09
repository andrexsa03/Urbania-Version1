from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    LoginView,
    RegisterView,
    LogoutView,
    PasswordRecoveryView,
    TwoFactorAuthView,
    health_check
)

app_name = 'auth'

urlpatterns = [
    # Authentication endpoints
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-recovery/', PasswordRecoveryView.as_view(), name='password_recovery'),
    path('two-factor/', TwoFactorAuthView.as_view(), name='two_factor_auth'),
    
    # Health check endpoint
    path('health/', health_check, name='health_check'),
]
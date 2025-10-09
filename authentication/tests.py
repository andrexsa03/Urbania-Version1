from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json

User = get_user_model()


class AuthenticationTestCase(APITestCase):
    """Test cases for authentication endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(
            email=self.user_data['email'],
            password=self.user_data['password'],
            first_name=self.user_data['first_name'],
            last_name=self.user_data['last_name']
        )
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        url = reverse('authentication:register')
        data = {
            'email': 'newuser@example.com',
            'password': 'NewPassword123!',
            'password_confirm': 'NewPassword123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        self.assertIn('email_sent', response.data)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        url = reverse('auth:register')
        data = {
            'email': 'newuser@example.com',
            'password': 'NewPassword123!',
            'password_confirm': 'DifferentPassword123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)
    
    def test_user_registration_duplicate_email(self):
        """Test registration with existing email"""
        url = reverse('auth:register')
        data = {
            'email': self.user_data['email'],  # Existing email
            'password': 'NewPassword123!',
            'password_confirm': 'NewPassword123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_user_login_success(self):
        """Test successful user login"""
        url = reverse('authentication:login')
        data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])
        self.assertIn('user', response.data)
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('authentication:login')
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_user_login_nonexistent_user(self):
        """Test login with non-existent user"""
        url = reverse('authentication:login')
        data = {
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_password_recovery_endpoint(self):
        """Test password recovery endpoint (dummy implementation)"""
        url = reverse('authentication:password-recovery')
        data = {'email': self.user_data['email']}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Password recovery email sent successfully')
    
    def test_password_recovery_invalid_email(self):
        """Test password recovery with invalid email format"""
        url = reverse('authentication:password-recovery')
        data = {'email': 'invalid-email'}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_two_factor_auth_endpoint(self):
        """Test two-factor authentication endpoint (mock implementation)"""
        url = reverse('authentication:two-factor-auth')
        data = {
            'email': self.user_data['email'],
            'code': '123456'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], '2FA verification successful')
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_two_factor_auth_invalid_code(self):
        """Test 2FA with invalid code format"""
        url = reverse('authentication:two-factor-auth')
        data = {
            'email': self.user_data['email'],
            'code': '12345'  # Too short
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('code', response.data)
    
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        url = reverse('authentication:health-check')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('status', response.data)
        self.assertEqual(response.data['status'], 'healthy')


class AuthSerializerTestCase(TestCase):
    """Test cases for authentication serializers"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'email': 'test@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
    
    def test_login_serializer_valid_data(self):
        """Test LoginSerializer with valid data"""
        from auth.serializers import LoginSerializer
        
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_login_serializer_invalid_password(self):
        """Test LoginSerializer with invalid password"""
        from auth.serializers import LoginSerializer
        
        data = {
            'email': self.user_data['email'],
            'password': 'WrongPassword'
        }
        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
    
    def test_register_serializer_valid_data(self):
        """Test RegisterSerializer with valid data"""
        from auth.serializers import RegisterSerializer
        
        data = {
            'email': 'newuser@example.com',
            'password': 'NewPassword123!',
            'password_confirm': 'NewPassword123!',
            'first_name': 'New',
            'last_name': 'User',
            'profile': {
                'phone_number': '+525512345678',
                'date_of_birth': '1990-01-01'
            }
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_register_serializer_password_mismatch(self):
        """Test RegisterSerializer with password mismatch"""
        from auth.serializers import RegisterSerializer
        
        data = {
            'email': 'newuser@example.com',
            'password': 'NewPassword123!',
            'password_confirm': 'DifferentPassword123!',
            'first_name': 'New',
            'last_name': 'User'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password_confirm', serializer.errors)

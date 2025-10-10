from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io
from users.models import UserProfile, Inmobiliaria
from roles.models import Role, Permission

User = get_user_model()


class UserManagementTestCase(APITestCase):
    """Test cases for user management endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test users
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='UserPassword123!',
            first_name='Regular',
            last_name='User'
        )
        
        # Create test role and permission
        self.permission = Permission.objects.create(
            name='Can manage users',
            codename='manage_users'
        )
        self.role = Role.objects.create(
            name='User Manager',
            description='Can manage user accounts'
        )
        self.role.permissions.add(self.permission)
    
    def authenticate_user(self, user):
        """Helper method to authenticate a user"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_user_list_as_admin(self):
        """Test user list endpoint as admin"""
        self.authenticate_user(self.admin_user)
        url = reverse('users:user-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_user_list_as_regular_user(self):
        """Test user list endpoint as regular user (should be forbidden)"""
        self.authenticate_user(self.regular_user)
        url = reverse('users:user-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_detail_as_owner(self):
        """Test user detail endpoint as owner"""
        self.authenticate_user(self.regular_user)
        url = reverse('users:user-detail', kwargs={'pk': self.regular_user.pk})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.regular_user.email)
    
    def test_user_detail_as_admin(self):
        """Test user detail endpoint as admin"""
        self.authenticate_user(self.admin_user)
        url = reverse('users:user-detail', kwargs={'pk': self.regular_user.pk})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.regular_user.email)
    
    def test_user_detail_unauthorized(self):
        """Test user detail endpoint without authentication"""
        url = reverse('users:user-detail', kwargs={'pk': self.regular_user.pk})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_me_endpoint(self):
        """Test current user endpoint"""
        self.authenticate_user(self.regular_user)
        url = reverse('users:user-me')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.regular_user.email)
    
    def test_user_create_as_admin(self):
        """Test user creation as admin"""
        self.authenticate_user(self.admin_user)
        url = reverse('users:user-list')
        data = {
            'email': 'newuser@example.com',
            'password': 'NewPassword123!',
            'first_name': 'New',
            'last_name': 'User',
            'profile': {
                'phone_number': '+525512345678',
                'date_of_birth': '1990-01-01'
            }
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_user_update_as_owner(self):
        """Test user update as owner"""
        self.authenticate_user(self.regular_user)
        url = reverse('users:user-detail', kwargs={'pk': self.regular_user.pk})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, 'Updated')
    
    def test_user_delete_as_admin(self):
        """Test user deletion as admin"""
        self.authenticate_user(self.admin_user)
        url = reverse('users:user-detail', kwargs={'pk': self.regular_user.pk})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.regular_user.pk).exists())
    
    def test_assign_role_to_user(self):
        """Test role assignment to user"""
        self.authenticate_user(self.admin_user)
        url = reverse('users:user-assign-role', kwargs={'pk': self.regular_user.pk})
        data = {'role_id': self.role.id}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.regular_user.roles.filter(id=self.role.id).exists())
    
    def test_password_change(self):
        """Test password change endpoint"""
        self.authenticate_user(self.regular_user)
        url = reverse('users:password-change')
        data = {
            'old_password': 'UserPassword123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password was changed
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password('NewPassword123!'))
    
    def test_password_change_wrong_old_password(self):
        """Test password change with wrong old password"""
        self.authenticate_user(self.regular_user)
        url = reverse('users:password-change')
        data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_stats_as_admin(self):
        """Test user statistics endpoint as admin"""
        self.authenticate_user(self.admin_user)
        url = reverse('users:user-stats')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
        self.assertIn('active_users', response.data)
        self.assertIn('inactive_users', response.data)


class UserProfileTestCase(APITestCase):
    """Test cases for user profile management"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testupdate@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        self.authenticate_user(self.user)
    
    def authenticate_user(self, user):
        """Helper method to authenticate a user"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_get_user_profile(self):
        """Test getting user profile"""
        url = reverse('users:profile')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], self.user.email)
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        url = reverse('users:profile')
        data = {
            'phone_number': '+525512345678',
            'date_of_birth': '1990-01-01',
            'bio': 'Updated bio'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify profile was updated
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(str(profile.phone_number), '+525512345678')
        self.assertEqual(profile.bio, 'Updated bio')


class UserSerializerTestCase(TestCase):
    """Test cases for user serializers"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
    
    def test_user_detail_serializer(self):
        """Test UserDetailSerializer"""
        from users.serializers import UserDetailSerializer
        
        serializer = UserDetailSerializer(instance=self.user)
        data = serializer.data
        
        self.assertEqual(data['email'], self.user.email)
        self.assertEqual(data['first_name'], self.user.first_name)
        self.assertIn('profile', data)
    
    def test_user_create_serializer(self):
        """Test UserCreateSerializer"""
        from users.serializers import UserCreateSerializer
        
        data = {
            'email': 'newuser@example.com',
            'password': 'NewPassword123!',
            'first_name': 'New',
            'last_name': 'User',
            'profile': {
                'phone_number': '+525512345678',
                'date_of_birth': '1990-01-01'
            }
        }
        
        serializer = UserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())
    
    def test_password_change_serializer(self):
        """Test PasswordChangeSerializer"""
        from users.serializers import PasswordChangeSerializer
        
        data = {
            'old_password': 'TestPassword123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        
        serializer = PasswordChangeSerializer(data=data, context={'user': self.user})
        self.assertTrue(serializer.is_valid())
    
    def test_password_change_serializer_mismatch(self):
        """Test PasswordChangeSerializer with password mismatch"""
        from users.serializers import PasswordChangeSerializer
        
        data = {
            'old_password': 'TestPassword123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'DifferentPassword123!'
        }
        
        serializer = PasswordChangeSerializer(data=data, context={'user': self.user})
        self.assertFalse(serializer.is_valid())
        self.assertIn('new_password_confirm', serializer.errors)


class InmobiliariaTestCase(APITestCase):
    """Test cases for Inmobiliaria model and endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
    def test_inmobiliaria_registration(self):
        """Test inmobiliaria registration endpoint"""
        url = reverse('auth:register_inmobiliaria')
        data = {
            'nombre': 'Inmobiliaria Test',
            'email': 'test@inmobiliaria.com',
            'telefono': '+34123456789',
            'direccion': 'Calle Test 123',
            'ciudad': 'Ciudad Test',
            'pais': 'País Test'
        }
        
        response = self.client.post(url, data, format='json')
        print(f"Response status: {response.status_code}")
        print(f"Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('inmobiliaria', response.data)
        
    def test_inmobiliaria_registration_duplicate_email(self):
        """Test inmobiliaria registration with duplicate email"""
        from users.models import Inmobiliaria
        
        # Create first inmobiliaria
        Inmobiliaria.objects.create(
            nombre='Primera Inmobiliaria',
            email='test@inmobiliaria.com',
            telefono='+34123456789'
        )
        
        url = reverse('auth:register_inmobiliaria')
        data = {
            'nombre': 'Segunda Inmobiliaria',
            'email': 'test@inmobiliaria.com',  # Same email
            'telefono': '+34987654321'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_inmobiliaria_registration_invalid_data(self):
        """Test inmobiliaria registration with invalid data"""
        url = reverse('auth:register_inmobiliaria')
        data = {
            'nombre': '',  # Empty name
            'email': 'invalid-email',  # Invalid email
            'telefono': 'invalid-phone'  # Invalid phone
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class UserProfileUpdateTestCase(APITestCase):
    """Test cases for user profile update endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='testportal@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        # UserProfile is automatically created by signal
        
    def authenticate_user(self, user):
        """Helper method to authenticate a user"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
    def test_profile_update(self):
        """Test profile update endpoint"""
        self.authenticate_user(self.user)
        
        url = reverse('user-profile-update')
        data = {
            'phone_number': '+34612345678',
            'bio': 'Updated bio',
            'website': 'https://example.com'
        }
        
        response = self.client.put(url, data, format='json')
        print(f"Profile update - Response status: {response.status_code}")
        print(f"Profile update - Response data: {response.data}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('profile', response.data)
        
    def test_profile_update_unauthorized(self):
        """Test profile update without authentication"""
        url = reverse('users:user-profile-update')
        data = {
            'bio': 'Updated bio'
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_profile_photo_upload(self):
        """Test profile photo upload endpoint"""
        self.authenticate_user(self.user)
        
        # Create a simple test image file
        from django.core.files.uploadedfile import SimpleUploadedFile
        from PIL import Image
        import io
        
        # Create a simple test image
        image = Image.new('RGB', (100, 100), color='red')
        image_file = io.BytesIO()
        image.save(image_file, format='JPEG')
        image_file.seek(0)
        
        uploaded_file = SimpleUploadedFile(
            "test_image.jpg",
            image_file.getvalue(),
            content_type="image/jpeg"
        )
        
        url = reverse('user-profile-photo')
        response = self.client.post(url, {'avatar': uploaded_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
    def test_profile_photo_upload_invalid_file(self):
        """Test profile photo upload with invalid file type"""
        self.authenticate_user(self.user)
        
        # Create a text file instead of image
        text_file = SimpleUploadedFile(
            "test.txt",
            b"This is not an image",
            content_type="text/plain"
        )
        
        url = reverse('users:user-profile-photo')
        response = self.client.post(url, {'avatar': text_file}, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)


class UserPortalProfileTestCase(APITestCase):
    """Test cases for user portal profile endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        
    def authenticate_user(self, user):
        """Helper method to authenticate a user"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
    def test_get_portal_profile(self):
        """Test get portal profile endpoint"""
        self.authenticate_user(self.user)
        
        url = reverse('user-portal-profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email', response.data)
        self.assertIn('full_name', response.data)
        
    def test_update_portal_profile(self):
        """Test update portal profile endpoint"""
        self.authenticate_user(self.user)
        
        url = reverse('user-portal-profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('profile', response.data)
        
    def test_portal_profile_unauthorized(self):
        """Test portal profile endpoints without authentication"""
        url = reverse('users:user-portal-profile')
        
        # Test GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test PUT
        response = self.client.put(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

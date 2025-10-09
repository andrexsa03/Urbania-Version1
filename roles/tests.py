from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from roles.models import Role, Permission, UserRole

User = get_user_model()


class RoleManagementTestCase(APITestCase):
    """Test cases for role management endpoints"""
    
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
        
        # Create test permissions
        self.permission1 = Permission.objects.create(
            name='Can view users',
            codename='view_users'
        )
        self.permission2 = Permission.objects.create(
            name='Can edit users',
            codename='edit_users'
        )
        
        # Create test role
        self.role = Role.objects.create(
            name='User Manager',
            description='Can manage user accounts'
        )
        self.role.permissions.add(self.permission1, self.permission2)
    
    def authenticate_user(self, user):
        """Helper method to authenticate a user"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_role_list_as_admin(self):
        """Test role list endpoint as admin"""
        self.authenticate_user(self.admin_user)
        url = reverse('roles:role-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_role_list_as_regular_user(self):
        """Test role list endpoint as regular user (should be forbidden)"""
        self.authenticate_user(self.regular_user)
        url = reverse('roles:role-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_role_detail_as_admin(self):
        """Test role detail endpoint as admin"""
        self.authenticate_user(self.admin_user)
        url = reverse('roles:role-detail', kwargs={'pk': self.role.pk})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.role.name)
        self.assertIn('permissions', response.data)
    
    def test_role_create_as_admin(self):
        """Test role creation as admin"""
        self.authenticate_user(self.admin_user)
        url = reverse('roles:role-list')
        data = {
            'name': 'Content Manager',
            'description': 'Can manage content',
            'permissions': [self.permission1.id]
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Role.objects.filter(name='Content Manager').exists())
    
    def test_role_update_as_admin(self):
        """Test role update as admin"""
        self.authenticate_user(self.admin_user)
        url = reverse('roles:role-detail', kwargs={'pk': self.role.pk})
        data = {
            'name': 'Updated Role Name',
            'description': 'Updated description'
        }
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.role.refresh_from_db()
        self.assertEqual(self.role.name, 'Updated Role Name')
    
    def test_role_delete_as_admin(self):
        """Test role deletion as admin"""
        self.authenticate_user(self.admin_user)
        url = reverse('roles:role-detail', kwargs={'pk': self.role.pk})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Role.objects.filter(pk=self.role.pk).exists())
    
    def test_role_add_permission(self):
        """Test adding permission to role"""
        self.authenticate_user(self.admin_user)
        
        # Create a new permission
        new_permission = Permission.objects.create(
            name='Can delete users',
            codename='delete_users'
        )
        
        url = reverse('roles:role-add-permission', kwargs={'pk': self.role.pk})
        data = {'permission_id': new_permission.id}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.role.permissions.filter(id=new_permission.id).exists())
    
    def test_role_remove_permission(self):
        """Test removing permission from role"""
        self.authenticate_user(self.admin_user)
        url = reverse('roles:role-remove-permission', kwargs={'pk': self.role.pk})
        data = {'permission_id': self.permission1.id}
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(self.role.permissions.filter(id=self.permission1.id).exists())
    
    def test_role_assigned_users(self):
        """Test getting users assigned to a role"""
        self.authenticate_user(self.admin_user)
        
        # Assign role to user
        UserRole.objects.create(user=self.regular_user, role=self.role)
        
        url = reverse('roles:role-assigned-users', kwargs={'pk': self.role.pk})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['email'], self.regular_user.email)


class PermissionManagementTestCase(APITestCase):
    """Test cases for permission management endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='User',
            is_staff=True,
            is_superuser=True
        )
        
        self.permission = Permission.objects.create(
            name='Can view reports',
            codename='view_reports'
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate a user"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_permission_list_as_admin(self):
        """Test permission list endpoint as admin"""
        self.authenticate_user(self.admin_user)
        url = reverse('roles:permission-list')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        # Check that at least our permission exists
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_permission_create_as_admin(self):
        """Test permission creation as admin"""
        self.authenticate_user(self.admin_user)
        url = reverse('roles:permission-list')
        data = {
            'name': 'Can export data',
            'codename': 'export_data'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Permission.objects.filter(codename='export_data').exists())
    
    def test_permission_create_duplicate_codename(self):
        """Test permission creation with duplicate codename"""
        self.authenticate_user(self.admin_user)
        url = reverse('roles:permission-list')
        data = {
            'name': 'Another permission',
            'codename': 'view_reports'  # Existing codename
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('codename', response.data)


class UserRoleManagementTestCase(APITestCase):
    """Test cases for user role assignment endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
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
        
        self.role = Role.objects.create(
            name='Test Role',
            description='Test role for assignments'
        )
    
    def authenticate_user(self, user):
        """Helper method to authenticate a user"""
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_assign_role_to_user(self):
        """Test assigning role to user"""
        self.authenticate_user(self.admin_user)
        url = reverse('roles:user-role-management')
        data = {
            'user_id': self.regular_user.id,
            'role_id': self.role.id,
            'action': 'assign'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(UserRole.objects.filter(user=self.regular_user, role=self.role).exists())
    
    def test_remove_role_from_user(self):
        """Test removing role from user"""
        self.authenticate_user(self.admin_user)
        
        # First assign the role
        UserRole.objects.create(user=self.regular_user, role=self.role)
        
        url = reverse('roles:user-role-management')
        data = {
            'user_id': self.regular_user.id,
            'role_id': self.role.id,
            'action': 'remove'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(UserRole.objects.filter(user=self.regular_user, role=self.role).exists())
    
    def test_user_role_history(self):
        """Test getting user role assignment history"""
        self.authenticate_user(self.admin_user)
        
        # Create role assignment
        UserRole.objects.create(user=self.regular_user, role=self.role)
        
        url = reverse('roles:user-role-history', kwargs={'user_id': self.regular_user.id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_role_stats(self):
        """Test role statistics endpoint"""
        self.authenticate_user(self.admin_user)
        
        # Create some role assignments
        UserRole.objects.create(user=self.regular_user, role=self.role)
        
        url = reverse('roles:role-stats')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_roles', response.data)
        self.assertIn('total_permissions', response.data)
        self.assertIn('total_assignments', response.data)


class RoleModelTestCase(TestCase):
    """Test cases for Role and Permission models"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='TestPassword123!',
            first_name='Test',
            last_name='User'
        )
        
        self.permission = Permission.objects.create(
            name='Test Permission',
            codename='test_permission'
        )
        
        self.role = Role.objects.create(
            name='Test Role',
            description='Test role description'
        )
        self.role.permissions.add(self.permission)
    
    def test_role_str_method(self):
        """Test Role __str__ method"""
        self.assertEqual(str(self.role), 'Test Role')
    
    def test_permission_str_method(self):
        """Test Permission __str__ method"""
        self.assertEqual(str(self.permission), 'Test Permission')
    
    def test_role_has_permission(self):
        """Test role has_permission method"""
        self.assertTrue(self.role.has_permission('test_permission'))
        self.assertFalse(self.role.has_permission('nonexistent_permission'))
    
    def test_user_role_assignment(self):
        """Test UserRole model"""
        user_role = UserRole.objects.create(user=self.user, role=self.role)
        
        self.assertEqual(str(user_role), f'{self.user.email} - {self.role.name}')
        self.assertTrue(user_role.is_active)
    
    def test_user_has_role_method(self):
        """Test User has_role method"""
        # Assign role to user
        UserRole.objects.create(user=self.user, role=self.role)
        
        self.assertTrue(self.user.has_role('Test Role'))
        self.assertFalse(self.user.has_role('Nonexistent Role'))
    
    def test_user_has_permission_method(self):
        """Test User has_permission method"""
        # Assign role to user
        UserRole.objects.create(user=self.user, role=self.role)
        
        self.assertTrue(self.user.has_permission('test_permission'))
        self.assertFalse(self.user.has_permission('nonexistent_permission'))
    
    def test_user_get_all_permissions_method(self):
        """Test User get_all_permissions method"""
        # Create another permission and role
        permission2 = Permission.objects.create(
            name='Another Permission',
            codename='another_permission'
        )
        role2 = Role.objects.create(
            name='Another Role',
            description='Another test role'
        )
        role2.permissions.add(permission2)
        
        # Assign both roles to user
        UserRole.objects.create(user=self.user, role=self.role)
        UserRole.objects.create(user=self.user, role=role2)
        
        permissions = self.user.get_all_permissions()
        self.assertEqual(len(permissions), 2)
        self.assertIn('test_permission', permissions)
        self.assertIn('another_permission', permissions)

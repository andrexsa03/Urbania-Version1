from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class Permission(models.Model):
    """
    Permission model to define specific permissions in the system.
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    codename = models.CharField(_('codename'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True, null=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Permission')
        verbose_name_plural = _('Permissions')
        db_table = 'roles_permission'
        ordering = ['name']

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    Role model to group permissions and assign them to users.
    """
    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True, null=True)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='roles',
        verbose_name=_('permissions')
    )
    is_active = models.BooleanField(_('active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('Role')
        verbose_name_plural = _('Roles')
        db_table = 'roles_role'
        ordering = ['name']

    def __str__(self):
        return self.name

    def add_permission(self, permission):
        """Add a permission to this role."""
        self.permissions.add(permission)

    def remove_permission(self, permission):
        """Remove a permission from this role."""
        self.permissions.remove(permission)

    def has_permission(self, permission_codename):
        """Check if this role has a specific permission."""
        return self.permissions.filter(codename=permission_codename).exists()

    @property
    def permission_list(self):
        """Return a list of permission codenames for this role."""
        return list(self.permissions.values_list('codename', flat=True))


class UserRole(models.Model):
    """
    Many-to-many relationship between Users and Roles with additional fields.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name=_('user')
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name=_('role')
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_roles',
        verbose_name=_('assigned by')
    )
    assigned_at = models.DateTimeField(_('assigned at'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        verbose_name = _('User Role')
        verbose_name_plural = _('User Roles')
        db_table = 'roles_userrole'
        unique_together = ['user', 'role']
        ordering = ['-assigned_at']

    def __str__(self):
        return f"{self.user.email} - {self.role.name}"


# Add methods to User model for role management
def add_role(self, role, assigned_by=None):
    """Add a role to the user."""
    user_role, created = UserRole.objects.get_or_create(
        user=self,
        role=role,
        defaults={'assigned_by': assigned_by, 'is_active': True}
    )
    if not created and not user_role.is_active:
        user_role.is_active = True
        user_role.assigned_by = assigned_by
        user_role.save()
    return user_role


def remove_role(self, role):
    """Remove a role from the user."""
    try:
        user_role = UserRole.objects.get(user=self, role=role)
        user_role.is_active = False
        user_role.save()
        return True
    except UserRole.DoesNotExist:
        return False


def has_role(self, role_name):
    """Check if the user has a specific role."""
    return self.user_roles.filter(
        role__name=role_name,
        is_active=True
    ).exists()


def has_permission(self, permission_codename):
    """Check if the user has a specific permission through their roles."""
    return UserRole.objects.filter(
        user=self,
        is_active=True,
        role__is_active=True,
        role__permissions__codename=permission_codename
    ).exists()


def get_roles(self):
    """Get all active roles for the user."""
    return Role.objects.filter(
        user_roles__user=self,
        user_roles__is_active=True,
        is_active=True
    )


def get_permissions(self):
    """Get all permissions for the user through their roles."""
    return Permission.objects.filter(
        roles__user_roles__user=self,
        roles__user_roles__is_active=True,
        roles__is_active=True
    ).distinct()


# Add methods to User model
User.add_to_class('add_role', add_role)
User.add_to_class('remove_role', remove_role)
User.add_to_class('has_role', has_role)
User.add_to_class('has_permission', has_permission)
User.add_to_class('get_roles', get_roles)
User.add_to_class('get_permissions', get_permissions)

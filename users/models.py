from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """
    Custom user manager that uses email as the unique identifier
    instead of username.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model that uses email as the unique identifier
    instead of username.
    """
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    is_email_verified = models.BooleanField(_('email verified'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        db_table = 'users_user'

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        """Return the full name of the user."""
        return f"{self.first_name} {self.last_name}".strip()


class UserProfile(models.Model):
    """
    Extended user profile with additional information.
    """
    GENDER_CHOICES = [
        ('M', _('Male')),
        ('F', _('Female')),
        ('O', _('Other')),
        ('N', _('Prefer not to say')),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('user')
    )
    phone_number = PhoneNumberField(
        _('phone number'),
        blank=True,
        null=True,
        help_text=_('Phone number in international format')
    )
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    gender = models.CharField(
        _('gender'),
        max_length=1,
        choices=GENDER_CHOICES,
        blank=True,
        null=True
    )
    address = models.TextField(_('address'), blank=True, null=True)
    city = models.CharField(_('city'), max_length=100, blank=True, null=True)
    country = models.CharField(_('country'), max_length=100, blank=True, null=True)
    postal_code = models.CharField(_('postal code'), max_length=20, blank=True, null=True)
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True
    )
    bio = models.TextField(_('bio'), max_length=500, blank=True, null=True)
    website = models.URLField(_('website'), blank=True, null=True)
    is_public = models.BooleanField(_('public profile'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        db_table = 'users_userprofile'

    def __str__(self):
        return f"{self.user.email} - Profile"

    @property
    def age(self):
        """Calculate and return the user's age."""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None


# Signal to create UserProfile when User is created
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()


class Inmobiliaria(models.Model):
    """
    Modelo para representar una inmobiliaria en el sistema CRM URBANY.
    Contiene la información corporativa necesaria para el registro.
    """
    nombre = models.CharField(
        _('nombre'),
        max_length=200,
        help_text=_('Nombre de la inmobiliaria')
    )
    email = models.EmailField(
        _('email'),
        unique=True,
        help_text=_('Email corporativo de la inmobiliaria')
    )
    telefono = PhoneNumberField(
        _('teléfono'),
        help_text=_('Teléfono de contacto en formato internacional')
    )
    direccion = models.TextField(
        _('dirección'),
        blank=True,
        null=True,
        help_text=_('Dirección física de la inmobiliaria')
    )
    ciudad = models.CharField(
        _('ciudad'),
        max_length=100,
        blank=True,
        null=True
    )
    pais = models.CharField(
        _('país'),
        max_length=100,
        blank=True,
        null=True
    )
    codigo_postal = models.CharField(
        _('código postal'),
        max_length=20,
        blank=True,
        null=True
    )
    sitio_web = models.URLField(
        _('sitio web'),
        blank=True,
        null=True
    )
    descripcion = models.TextField(
        _('descripción'),
        max_length=1000,
        blank=True,
        null=True,
        help_text=_('Descripción de la inmobiliaria')
    )
    logo = models.ImageField(
        _('logo'),
        upload_to='inmobiliarias/logos/',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        _('activa'),
        default=True,
        help_text=_('Indica si la inmobiliaria está activa en el sistema')
    )
    fecha_registro = models.DateTimeField(
        _('fecha de registro'),
        auto_now_add=True
    )
    fecha_actualizacion = models.DateTimeField(
        _('fecha de actualización'),
        auto_now=True
    )

    class Meta:
        verbose_name = _('Inmobiliaria')
        verbose_name_plural = _('Inmobiliarias')
        db_table = 'users_inmobiliaria'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    @property
    def direccion_completa(self):
        """
        Retorna la dirección completa concatenada.
        """
        partes = [self.direccion, self.ciudad, self.pais, self.codigo_postal]
        return ', '.join(filter(None, partes))


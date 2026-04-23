# usuarios/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User

# 1. Definimos los roles primero para que la clase Usuario los reconozca
ROLES = (
    ('cliente', 'Cliente'),
    ('barbero', 'Barbero'),
    ('admin', 'Administrador'),
)

# 2. Una SOLA clase Usuario con todos tus campos unidos
class Usuario(AbstractUser):
    # Usamos el campo username por defecto pero lo adaptamos para que sea el documento
    username = models.CharField(
        max_length=20, unique=True, verbose_name="Número de Documento"
    )
    telefono = models.CharField(max_length=15, verbose_name="Teléfono")
    email = models.EmailField(unique=True) # Hacemos el email único
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    especialidad = models.CharField(max_length=100, blank=True, null=True)

    # Estos campos son necesarios para que Django sepa cómo manejar el login
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.rol})"

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

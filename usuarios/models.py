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
    nombre_completo = models.CharField(max_length=150, verbose_name="Nombre Completo")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono")
    email = models.EmailField(unique=True) # Hacemos el email único
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')

    # Estos campos son necesarios para que Django sepa cómo manejar el login
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'nombre_completo']

    def __str__(self):
        return f"{self.nombre_completo} ({self.rol})"

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

# 3. El modelo Barbero (que es independiente para tu lista de calificación)
class Barbero(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Barbero")
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre


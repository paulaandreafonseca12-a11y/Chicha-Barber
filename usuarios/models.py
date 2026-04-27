from django.contrib.auth.models import AbstractUser
from django.db import models

# Definimos los roles fuera o dentro de la clase, está bien así.
ROLES = (
    ('cliente', 'Cliente'),
    ('barbero', 'Barbero'),
    ('admin', 'Administrador'),
)

class Usuario(AbstractUser):
    # El documento será el 'username' interno de Django
    username = models.CharField(
        max_length=20, 
        unique=True, 
        verbose_name="Número de Documento"
    )
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, verbose_name="Teléfono")
    rol = models.CharField(max_length=20, choices=ROLES, default='cliente')
    
    # Campo específico para barberos
    especialidad = models.CharField(max_length=100, blank=True, null=True)

    # Configuración de Login: Entrarán con el EMAIL
    USERNAME_FIELD = 'email'
    # Campos que pide el comando 'createsuperuser' (no incluyas el EMAIL ni el PASSWORD aquí)
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.get_full_name()} ({self.get_rol_display()})"

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
from django.db import models
from servicios.models import Servicios
from django.contrib.auth.models import User

class Reserva(models.Model):
    nombre_cliente = models.CharField(max_length=100, verbose_name="Nombre del Cliente")
    correo_cliente = models.EmailField(verbose_name="Correo Electrónico")
    telefono_cliente = models.CharField(max_length=20, verbose_name="Teléfono")
    fecha_reserva = models.DateTimeField(verbose_name="Fecha y Hora")
    # Relacionamos con el modelo Servicios que ya tienes
    servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE, related_name='reservas_detalle')
    
    ESTADO_CHOICES = [
        ('reservada', 'Reservada'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='reservada')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_cliente} - {self.servicio.nombre}"

from django.db import models
from django.conf import settings # Importante para usar AUTH_USER_MODEL
from servicios.models import Servicios

class Calificacion(models.Model):
    # CORRECCIÓN: Apuntar al modelo de usuario configurado en el proyecto
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    puntuacion = models.IntegerField(verbose_name="Estrellas")
    resena = models.TextField(verbose_name="Comentario")
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username if self.usuario else 'Anónimo'} - {self.puntuacion} estrellas"
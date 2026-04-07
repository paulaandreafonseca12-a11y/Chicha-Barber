
from django.db import models
# 1. IMPORTANTE: Traemos el modelo Barbero de tu otra aplicación
from usuarios.models import Barbero 
# Create your models here.

class Reserva(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    fecha_reserva = models.DateTimeField()
    servicio = models.CharField(max_length=100)
    def __str__(self):
        return f"Reserva de {self.nombre_cliente} para {self.servicio} el {self.fecha_reserva}"
    
    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
    
    ESTADO_CHOICES = [
        ('reservada', 'Reservada'),
        ('cancelada', 'Cancelada'),
    ]
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='reservada'
    )
    
class Calificacion(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    servicio_calificado = models.CharField(max_length=100)
    calificacion = models.IntegerField()
    comentario = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"

    def __str__(self):
        return f"Calificación de {self.nombre_cliente} para {self.servicio_calificado}: {self.calificacion} estrellas"
    

class Calificacion(models.Model):
    # 2. Corregido: 'on_delete' en lugar de 'on_status'
    barbero_a_calificar = models.ForeignKey(Barbero, on_delete=models.CASCADE)
    calificacion = models.IntegerField()
    resenia = models.TextField()

    def __str__(self):
        return f"Calificación para {self.barbero_a_calificar.nombre}"
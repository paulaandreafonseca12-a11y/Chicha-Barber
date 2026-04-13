from django.db import models
# Importamos el modelo Barbero de tu aplicación de usuarios
from usuarios.models import Barbero 


class Reserva(models.Model):
    nombre_cliente = models.CharField(max_length=100, verbose_name="Nombre del Cliente")
    correo_cliente = models.EmailField(verbose_name="Correo Electrónico")
    telefono_cliente = models.CharField(max_length=20, verbose_name="Teléfono")
    fecha_reserva = models.CharField(max_length=150, verbose_name="Fecha y Hora")
    servicio = models.CharField(max_length=100, default="Corte de Cabello")
    
    ESTADO_CHOICES = [
        ('reservada', 'Reservada'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='reservada')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_cliente} - {self.fecha_reserva}"
    
class Calificacion(models.Model):
    # Relación con el barbero que trabaja en Chicha Barber
    barbero_a_calificar = models.ForeignKey(Barbero, on_delete=models.CASCADE)
    nombre_cliente = models.CharField(max_length=100, default="Anónimo")
    calificacion = models.IntegerField() # Escala de 1 a 5
    resenia = models.TextField(verbose_name="Reseña")

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"

    def __str__(self):
        return f"Reseña para {self.barbero_a_calificar.nombre} - {self.calificacion}★"

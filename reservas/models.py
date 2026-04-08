from django.db import models
from servicios.models import Servicios 
# Create your models here.

class Reserva(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    fecha_reserva = models.DateTimeField()
    # RELACIÓN: Una reserva pertenece a un Servicio
    servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE, related_name='reservas')
    
    # Campo extra útil: saber cuándo se creó la reserva
    creado_el = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

    def __str__(self):
        return f"Reserva de {self.nombre_cliente} - {self.servicio.nombre} ({self.fecha_reserva})"
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
    
    


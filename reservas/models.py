from django.db import models

# Create your models here.

class Reserva(models.Model):
    nombre_cliente = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    fecha_reserva = models.DateTimeField()
    servicio = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"

    def __str__(self):
        return f"Reserva de {self.nombre_cliente} para {self.servicio} el {self.fecha_reserva}"
    
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
    
    


from django.db import models
from servicios.models import Servicios
from usuarios.models import Usuario


# =========================
# RESERVAS
# =========================
class Reserva(models.Model):

    nombre_cliente = models.CharField(
        max_length=100,
        verbose_name="Nombre del Cliente"
    )

    correo_cliente = models.EmailField(
        verbose_name="Correo Electrónico"
    )

    telefono_cliente = models.CharField(
        max_length=20,
        verbose_name="Teléfono"
    )

    # Fecha y hora REAL de la reserva
    fecha_reserva = models.DateTimeField(
        verbose_name="Fecha y Hora de la Reserva"
    )

    # Relación con servicios
    servicio = models.ForeignKey(
        Servicios,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name="Servicio"
    )

    ESTADO_CHOICES = [
        ('reservada', 'Reservada'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
    ]

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='reservada',
        verbose_name="Estado"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación"
    )

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha_reserva']

    def __str__(self):
        return f"{self.nombre_cliente} - {self.servicio.nombre} ({self.fecha_reserva})"


# =========================
# CALIFICACIONES
# =========================
class Calificacion(models.Model):

    # Relación con el barbero
    barbero_a_calificar = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        verbose_name="Barbero"
    )

    nombre_cliente = models.CharField(
        max_length=100,
        default="Anónimo",
        verbose_name="Cliente"
    )

    # Escala de 1 a 5
    calificacion = models.IntegerField(
        verbose_name="Calificación"
    )

    resenia = models.TextField(
        verbose_name="Reseña"
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Reseña para {self.barbero_a_calificar.first_name} {self.barbero_a_calificar.last_name} - {self.calificacion}★"
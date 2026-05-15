from datetime import datetime

from django.db import models
from django.utils import timezone
from servicios.models import Servicios
from usuarios.models import Usuario


# =========================
# TURNOS
# =========================
class Turno(models.Model):

    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('reservado', 'Reservado'),
        ('cancelado', 'Cancelado'),
    ]

    profesional = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='turnos',
        verbose_name='Profesional'
    )
    fecha = models.DateField(
        verbose_name='Fecha del Turno'
    )
    hora_inicio = models.TimeField(
        verbose_name='Hora de Inicio'
    )
    hora_fin = models.TimeField(
        verbose_name='Hora de Fin'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='disponible',
        verbose_name='Estado'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Creación'
    )

    class Meta:
        verbose_name = 'Turno'
        verbose_name_plural = 'Turnos'
        ordering = ['fecha', 'hora_inicio']

    def __str__(self):
        return f"{self.profesional.get_full_name()} - {self.fecha} {self.hora_inicio} a {self.hora_fin} ({self.estado})"


# =========================
# RESERVAS
# =========================
class Reserva(models.Model):

    turno = models.ForeignKey(
        'Turno',
        on_delete=models.SET_NULL,
        related_name='reservas',
        null=True,
        blank=True,
        verbose_name='Turno'
    )

    cliente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name='reservas_cliente',
        null=True,
        blank=True,
        verbose_name='Cliente'
    )

    nombre_cliente = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nombre del Cliente"
    )

    correo_cliente = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Correo Electrónico"
    )

    telefono_cliente = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Teléfono"
    )

    # Fecha y hora REAL de la reserva
    fecha_reserva = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Fecha y Hora de la Reserva"
    )

    precio_historico = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Precio Histórico'
    )

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

    def save(self, *args, **kwargs):
        if self.turno and not self.fecha_reserva:
            self.fecha_reserva = timezone.make_aware(datetime.combine(self.turno.fecha, self.turno.hora_inicio))
        super().save(*args, **kwargs)

    def __str__(self):
        cliente_nombre = self.nombre_cliente or (self.cliente.get_full_name() if self.cliente else 'Sin cliente')
        fecha = self.fecha_reserva or (self.turno.fecha if self.turno else 'Sin fecha')
        return f"{cliente_nombre} - {self.servicio.nombre} ({fecha})"


# =========================
# CALIFICACIONES
# =========================
class Calificacion(models.Model):

    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='calificaciones',
        null=True,
        blank=True,
        verbose_name='Reserva'
    )
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

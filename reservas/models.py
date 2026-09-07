from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from servicios.models import Servicios
from catalogo.models import Promocion

from usuarios.models import (
    Notificacion,
    HistorialAccion,
    Usuario,
)


# ==========================================================
# 1. AGENDA
# ==========================================================

class Agenda(models.Model):

    ESTADO_CHOICES = [
        ("disponible", "Disponible"),
        ("reservada", "Reservada"),
        ("cancelada", "Cancelada"),
    ]

    profesional = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="agendas",
        verbose_name="Profesional",
    )

    fecha = models.DateField(
        verbose_name="Fecha de la Agenda"
    )

    hora_inicio = models.TimeField(
        verbose_name="Hora de Inicio"
    )

    hora_fin = models.TimeField(
        verbose_name="Hora de Fin"
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="disponible",
        verbose_name="Estado",
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de Creación",
    )

    class Meta:
        verbose_name = "Agenda"
        verbose_name_plural = "Agendas"
        ordering = ["fecha", "hora_inicio"]

    def clean(self):

        super().clean()

        if (
            self.hora_inicio
            and self.hora_fin
            and self.hora_inicio >= self.hora_fin
        ):
            raise ValidationError({
                "hora_fin":
                    "La hora de fin debe ser posterior "
                    "a la hora de inicio."
            })

    def __str__(self):

        nombre = (
            self.profesional.get_full_name()
            if hasattr(
                self.profesional,
                "get_full_name"
            )
            and self.profesional.get_full_name()
            else str(self.profesional)
        )

        return (
            f"Agenda: {nombre} - "
            f"{self.fecha} "
            f"({self.hora_inicio} a {self.hora_fin}) "
            f"[{self.get_estado_display()}]"
        )


# ==========================================================
# 2. RESERVA
# ==========================================================

class Reserva(models.Model):

    ESTADO_CHOICES = [
        ("reservada", "Reservada"),
        ("confirmada", "Confirmada"),
        ("cancelada", "Cancelada"),
    ]

    agenda = models.ForeignKey(
        Agenda,
        on_delete=models.SET_NULL,
        related_name="reservas",
        null=True,
        blank=True,
        verbose_name="Agenda",
    )
    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="reservas_usuario",
        null=True,
        blank=True,
        verbose_name="Usuario",
    )

    servicio = models.ForeignKey(
        Servicios,
        on_delete=models.CASCADE,
        related_name="reservas",
        verbose_name="Servicio",
    )
    observacion = models.TextField(blank=True, null=True, verbose_name="Observación")
    estado = models.CharField(
        max_length=20, choices=ESTADO_CHOICES, default="reservada", verbose_name="Estado"
    )
    
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")

    # Campos para usuarios invitados o historial
    nombre_usuario = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nombre del Usuario (Invitado)")
    correo_usuario = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    telefono_usuario = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    fecha_reserva = models.DateTimeField(blank=True, null=True, verbose_name="Fecha y Hora de la Reserva")
    precio_historico = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Precio Histórico")

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = [
            "-fecha_reserva",
            "-fecha_creacion",
        ]

    def save(self, *args, **kwargs):

        if self.agenda and not self.fecha_reserva:

            fecha_hora = datetime.combine(
                self.agenda.fecha,
                self.agenda.hora_inicio,
            )

            if timezone.is_naive(fecha_hora):

                self.fecha_reserva = (
                    timezone.make_aware(
                        fecha_hora
                    )
                )

            else:
                self.fecha_reserva = fecha_hora

        super().save(*args, **kwargs)

    def __str__(self):
        usuario_nombre = self.nombre_usuario or (self.usuario.get_full_name() if self.usuario and hasattr(self.usuario, "get_full_name") else str(self.usuario or "Sin usuario"))
        fecha_str = self.fecha_reserva.strftime("%Y-%m-%d %H:%M") if self.fecha_reserva else (str(self.agenda.fecha) if self.agenda else "Sin fecha")
        return f"{usuario_nombre} - {self.servicio.nombre} ({fecha_str})"

# ==========================================================
# 3. NOTIFICACIÓN + HISTORIAL DE RESERVA
# ==========================================================

@receiver(post_save, sender=Reserva)
def notificar_reserva(
    sender,
    instance,
    created,
    **kwargs
):

    if not created:
        return

    usuario_nombre = instance.nombre_usuario or (
        instance.usuario.get_full_name() if instance.usuario and hasattr(instance.usuario, "get_full_name") and instance.usuario.get_full_name() else "Usuario"
    )

    if instance.usuario:
        Notificacion.objects.create(
            usuario=instance.usuario,
            tipo="reserva",
            mensaje=(
                f"Tu reserva de "
                f"{instance.servicio.nombre} "
                f"fue registrada con éxito."
            ),
            url="/perfil/",
        )

        HistorialAccion.objects.create(
            usuario=instance.cliente,
            reserva=instance,
            servicio=instance.servicio,
            tipo="reserva",
            accion="reservar",
            descripcion=(
                f"Realizó una reserva para "
                f"{instance.servicio.nombre}."
            ),
        )

    # ------------------------------------------------------
    # ADMINISTRADORES
    # ------------------------------------------------------

    admins = Usuario.objects.filter(
        Q(rol="admin") |
        Q(is_superuser=True)
    ).distinct()

    for admin in admins:

        Notificacion.objects.create(
            usuario=admin,
            reserva=instance,
            servicio=instance.servicio,
            tipo="reserva",
            mensaje=f"Nueva reserva de {usuario_nombre} para {instance.servicio.nombre}.",
            url="/admin-reservas/",
        )
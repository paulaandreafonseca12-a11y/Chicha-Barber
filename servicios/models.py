import os
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify  # type: ignore


def renombrar_imagen_servicio(instance, filename):
    ext = filename.split(".")[-1]
    nombre_limpio = slugify(instance.nombre)
    return os.path.join("servicios/", f"{nombre_limpio}_{instance.pk}.{ext}")


class Servicios(models.Model):
    nombre = models.CharField(max_length=150, verbose_name="Nombre")
    precio = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Precio"
    )
    duracion = models.IntegerField(verbose_name="Duración (minutos)")
    descripcion = models.TextField(verbose_name="Descripción")
    imagen = models.ImageField(
        upload_to=renombrar_imagen_servicio,
        null=True,
        blank=True,
        verbose_name="Imagen del servicio",
    )
    estado = models.BooleanField(default=True, verbose_name="Estado")

    class Meta:
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if self.pk is None and self.imagen:
            imagen_temp = self.imagen
            self.imagen = None
            super().save(*args, **kwargs)
            self.imagen = imagen_temp
            kwargs.pop("force_insert", None)
        super().save(*args, **kwargs)


def renombrar_imagen_promocion(instance, filename):
    ext = filename.split(".")[-1]
    nombre_limpio = slugify(instance.nombre)
    return os.path.join("promociones/", f"{nombre_limpio}_{instance.pk}.{ext}")



class Calificacion(models.Model):
    servicio = models.ForeignKey(
        Servicios,
        on_delete=models.CASCADE,
        related_name="calificaciones",
        verbose_name="Servicios",
    )
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calificaciones",
        verbose_name="Cliente",
    )
    cliente_nombre = models.CharField(
        max_length=150, verbose_name="Nombre del cliente (respaldo)"
    )
    puntuacion = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Puntuación",
    )
    comentario = models.TextField(verbose_name="Comentario")
    fecha_calificacion = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de calificación"
    )
    mostrar_en_inicio = models.BooleanField(
        default=False, verbose_name="Mostrar en inicio"
    )

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
        ordering = ["-fecha_calificacion"]

    def __str__(self):
        nombre = (
            self.cliente.get_full_name()
            if self.cliente and hasattr(self.cliente, "get_full_name")
            else self.cliente_nombre
        )
        return f"{nombre} - {self.servicio.nombre} ({self.puntuacion} estrellas)"

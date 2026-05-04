import os

from django.db import models # type: ignore

# Create your models here.


def carrusel_view(instance, filename):
    ext = filename.split('.')[-1]
    nombre_limpio = slugify(instance.nombre) # type: ignore
    return os.path.join('carrusel/', f"{nombre_limpio}_{instance.pk}.{ext}")

class Carrusel(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de modificación')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    imagen = models.ImageField(upload_to=carrusel_view, null=True, blank=True, verbose_name='Imagen del carrusel')
    texto = models.TextField(null=True, blank=True, verbose_name='Texto del carrusel')
    estado = models.BooleanField(default=True, verbose_name='Estado')
    

    class Meta:
        verbose_name = 'Carrusel'
        verbose_name_plural = 'Carruseles'
        
    def __str__(self):
        return self.nombre
        
    def save(self, *args, **kwargs):
        if self.pk is None and self.imagen:
            imagen_temp = self.imagen
            self.imagen = None
            super().save(*args, **kwargs)
            self.imagen = imagen_temp
        super().save(*args, **kwargs)



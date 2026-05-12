import os
from django.utils.text import slugify # type: ignore
from django.db import models # type: ignore

from django.contrib.auth.models import AbstractUser # type: ignore

def renombrar_imagen_servicio(instance, filename):
    ext = filename.split('.')[-1]
    nombre_limpio = slugify(instance.nombre)
    # Genera algo como: "servicios/corte-de-cabello_5.jpg"
    return os.path.join('servicios/', f"{nombre_limpio}_{instance.pk}.{ext}")

class Servicios(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    duracion = models.IntegerField(verbose_name='Duración (minutos)')
    descripcion = models.TextField(verbose_name='Descripción')
    imagen = models.ImageField(upload_to=renombrar_imagen_servicio, null=True, blank=True, verbose_name='Imagen del servicio')
    estado = models.BooleanField(default=True, verbose_name='Estado')

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        
    def __str__(self):
        return self.nombre
        
    def save(self, *args, **kwargs):
        # Si es un servicio nuevo, primero lo guardamos sin la imagen para que la BD le asigne un ID
        if self.pk is None and self.imagen:
            imagen_temp = self.imagen
            self.imagen = None
            super().save(*args, **kwargs)
            self.imagen = imagen_temp # Restauramos la imagen para guardarla con el ID generado
        super().save(*args, **kwargs)

def renombrar_imagen_promocion(instance, filename):
    ext = filename.split('.')[-1]
    nombre_limpio = slugify(instance.nombre)
    # Genera algo como: "promociones/descuento-verano_3.png"
    return os.path.join('promociones/', f"{nombre_limpio}_{instance.pk}.{ext}")
    
class Promocion(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='nombre')
    descuento = models.CharField(max_length=100, verbose_name='Descuento')
    duracion = models.CharField(max_length=30, verbose_name='Duración')
    descripcion = models.TextField(verbose_name='Descripcion')
    imagen = models.ImageField(upload_to=renombrar_imagen_promocion, null=True, blank=True, verbose_name='Imagen de la promoción')
    estado = models.BooleanField(default=True, verbose_name='Estado')

    class Meta:
        verbose_name = 'Promoción' #singular 
        verbose_name_plural = 'Promociones'# plural 
        
    def __str__(self):
        return self.nombre
        
    def save(self, *args, **kwargs):
        if self.pk is None and self.imagen:
            imagen_temp = self.imagen
            self.imagen = None
            super().save(*args, **kwargs)
            self.imagen = imagen_temp
        super().save(*args, **kwargs)

class CitaServicios(models.Model):
    
    codigo_cita = models.CharField(max_length=8, unique=True, verbose_name='Código de cita')
    cantidad=models.CharField(max_length=10, verbose_name='Cantidad')
    subtotal=models.CharField(max_length=10, verbose_name='Subtotal')
    servicio=models.ForeignKey(Servicios, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='servicio')
    # cita= models.ForeignKey('cita', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='cita')
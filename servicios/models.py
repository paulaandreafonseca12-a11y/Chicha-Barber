from django.db import models # type: ignore

from django.contrib.auth.models import AbstractUser # type: ignore


class Servicios(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    precio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    duracion = models.IntegerField(verbose_name='Duración (minutos)')
    descripcion = models.TextField(verbose_name='Descripción')

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'
        
    def __str__(self):
        return self.nombre
    
class promocion(models.Model):
    codigo_promocion = models.CharField(max_length=8, unique=True, verbose_name='Código de promoción')
    nombre = models.CharField(max_length=150, verbose_name='nombre')
    descuento = models.CharField(max_length=10, verbose_name='Descuento')
    duracion = models.CharField(max_length=20, verbose_name='Duración')
    descripcion = models.TextField(verbose_name='Descripción')
    cita_promocion = models.ForeignKey('promocion', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='cita_promocion')

    class Meta:
        verbose_name = 'Promoción' #singular 
        verbose_name_plural = 'Promociones'# plural 
        
    def __str__(self):
        return self.nombre


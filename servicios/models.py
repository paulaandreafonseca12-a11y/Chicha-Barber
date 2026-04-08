from django.db import models # type: ignore

from django.contrib.auth.models import AbstractUser # type: ignore


class Servicios(models.Model):
    
    codigo_servicios = models.CharField(max_length=8, unique=True, verbose_name='Código de servicios')
    nombre = models.CharField(max_length=150, verbose_name='nombre')
    precio = models.CharField(max_length=10, verbose_name='Precio')
    duracion = models.CharField(max_length=20, verbose_name='Duración')
    descripcion = models.TextField(verbose_name='Descripción')
    cita_servicios = models.ForeignKey('servicios', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='cita_servicios')

    class Meta:
        verbose_name = 'Servicio' #singular 
        verbose_name_plural = 'Servicios'# plural 
        
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


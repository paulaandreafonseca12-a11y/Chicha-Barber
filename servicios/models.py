from django.db import models # type: ignore

from django.contrib.auth.models import AbstractUser # type: ignore

class Servicios(models.Model):
    
    codigo_servicios = models.CharField(max_length=8, unique=True, verbose_name='Código de servicios')
    nombre = models.CharField(max_length=150, verbose_name='nombre')
    precio = models.CharField(max_length=10, verbose_name='Precio')
    duracion = models.CharField(max_length=20, verbose_name='Duración')
    descripcion = models.TextField(verbose_name='Descripción')
    imagen = models.ImageField(upload_to='servicios/', null=True, blank=True, verbose_name='Imagen del servicio')

    class Meta:
        verbose_name = 'Servicio' #singular 
        verbose_name_plural = 'Servicios'# plural 
        
    def __str__(self):
        return self.nombre
    
class Promocion(models.Model):
    nombre = models.CharField(max_length=150, verbose_name='nombre')
    descuento = models.CharField(max_length=100, verbose_name='Descuento')
    duracion = models.CharField(max_length=30, verbose_name='Duración')
    descripcion = models.TextField(verbose_name='Descripcion')

    class Meta:
        verbose_name = 'Promoción' #singular 
        verbose_name_plural = 'Promociones'# plural 
        
    def __str__(self):
        return self.nombre

class CitaServicios(models.Model):
    
    codigo_cita = models.CharField(max_length=8, unique=True, verbose_name='Código de cita')
    cantidad=models.CharField(max_length=10, verbose_name='Cantidad')
    subtotal=models.CharField(max_length=10, verbose_name='Subtotal')
    servicio=models.ForeignKey(Servicios, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='servicio')
    # cita= models.ForeignKey('cita', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='cita')
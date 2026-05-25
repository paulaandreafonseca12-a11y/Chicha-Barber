import os
from django.db import models # type: ignore
from django.utils.text import slugify # type: ignore
from PIL import Image # type: ignore

# Create your models here.


def carrusel_view(instance, filename):
    ext = filename.split('.')[-1]
    nombre_limpio = slugify(instance.nombre)
    return os.path.join('carrusel/', f"{nombre_limpio}_{instance.pk}.{ext}")


class Carrusel(models.Model):
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de creación')
    fecha_modificacion = models.DateTimeField(auto_now=True, verbose_name='Fecha de modificación')
    nombre = models.CharField(max_length=150, verbose_name='Nombre')
    imagen = models.ImageField(upload_to=carrusel_view, null=True, blank=True, verbose_name='Imagen del carrusel')
    texto = models.TextField(verbose_name='Texto alternativo (Alt)', default='Imagen de carrusel', help_text='Descripción obligatoria para accesibilidad y SEO')
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
            super().save(update_fields=['imagen']) # Save the image with the new pk
        else:
            super().save(*args, **kwargs)
            
        # Lógica para mantener máximo 4 carruseles activos
        if self.estado:
            active_carruseles = Carrusel.objects.filter(estado=True).order_by('fecha_modificacion')
            count = active_carruseles.count()
            if count > 4:
                # Desactivar los más antiguos (excluyendo el actual)
                to_deactivate_ids = list(active_carruseles.exclude(pk=self.pk).values_list('pk', flat=True)[:count - 4])
                if to_deactivate_ids:
                    Carrusel.objects.filter(pk__in=to_deactivate_ids).update(estado=False)
            
        if self.imagen:
            try:
                img = Image.open(self.imagen.path)
                target_size = (1200, 500)
                
                if img.size != target_size:
                    from PIL import ImageOps
                    
                    resample_filter = getattr(Image, 'Resampling', Image).LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
                    
                    # ImageOps.fit recorta y centra la imagen al tamaño especificado sin distorsionar
                    img = ImageOps.fit(img, target_size, method=resample_filter)
                    
                    if img.mode in ('RGBA', 'P') and self.imagen.path.lower().endswith(('.jpg', '.jpeg')):
                        img = img.convert('RGB')
                        
                    img.save(self.imagen.path)
            except Exception as e:
                print(f"Error al redimensionar la imagen: {e}")

def eliminar_carrusel(instance, filename):
    ext = filename.split('.')[-1]
    nombre_limpio = slugify(instance.nombre)
    return os.path.join('carrusel/', f"{nombre_limpio}_{instance.pk}_quitar.{ext}")

def editar_carrusel(instance, filename):
    ext = filename.split('.')[-1]
    nombre_limpio = slugify(instance.nombre)
    return os.path.join('carrusel/', f"{nombre_limpio}_{instance.pk}_editar.{ext}")



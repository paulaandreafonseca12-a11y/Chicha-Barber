import os
from django.db import models # type: ignore
from django.utils.text import slugify
from PIL import Image

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
            super().save(update_fields=['imagen']) # Save the image with the new pk
        else:
            super().save(*args, **kwargs)
            
        if self.imagen:
            try:
                img = Image.open(self.imagen.path)
                # Tamaño por defecto recomendado para carrusel
                target_size = (1200, 500)
                
                # Solo redimensionar si no es exactamente del tamaño
                if img.size != target_size:
                    # Usar Image.Resampling.LANCZOS si está disponible, sino Image.ANTIALIAS (versiones más antiguas de PIL)
                    resample_filter = getattr(Image, 'Resampling', Image).LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
                    
                    # Para evitar distorsión severa podemos hacer un resize con crop (cover)
                    # o simplemente forzar el resize. Ya que es un carrusel, a veces forzar el resize
                    # es lo que pide el usuario, pero lo ideal es un thumbnail que recorte.
                    from PIL import ImageOps
                    import PIL
                    
                    # Método simple: forzar dimensiones
                    img = img.resize(target_size, resample_filter)
                    img.save(self.imagen.path)
            except Exception as e:
                print(f"Error al redimensionar la imagen: {e}")




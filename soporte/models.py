from django.db import models
# 1. Importa settings en lugar del modelo User directo
from django.conf import settings 

class CategoriaAyuda(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    icono = models.CharField(max_length=50, help_text="Clase de FontAwesome o Bootstrap Icons")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nombre

class ArticuloFAQ(models.Model):
    categoria = models.ForeignKey(CategoriaAyuda, on_delete=models.CASCADE, related_name='articulos')
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    visitas = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.titulo

class TicketSoporte(models.Model):
    ESTADOS = [
        ('ABIERTO', 'Abierto'),
        ('PROCESO', 'En Proceso'),
        ('RESUELTO', 'Resuelto'),
    ]
    
    # 2. CAMBIA ESTA LÍNEA: Usa settings.AUTH_USER_MODEL
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    categoria = models.ForeignKey(CategoriaAyuda, on_delete=models.SET_NULL, null=True)
    asunto = models.CharField(max_length=200)
    descripcion = models.TextField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default='ABIERTO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.asunto}"
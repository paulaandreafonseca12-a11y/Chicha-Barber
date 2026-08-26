from django.contrib import admin # type: ignore
from .models import Servicios,Calificacion

admin.site.register(Servicios)
  
admin.site.register(Calificacion)

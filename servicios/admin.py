from django.contrib import admin # type: ignore
from .models import Servicios, Promocion, Calificacion

admin.site.register(Servicios)
admin.site.register(Promocion)  
admin.site.register(Calificacion)

from django.contrib import admin

from servicios.models import Promocion

# Register your models here.

from .models import Reserva, Calificacion

admin.site.register(Reserva)
admin.site.register(Calificacion)
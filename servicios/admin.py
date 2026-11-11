from django.contrib import admin # type: ignore
from .models import Calificacion, Servicios


@admin.register(Servicios)
class ServiciosAdmin(admin.ModelAdmin):
    search_fields = (
        "nombre",
        "descripcion",
    )


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    search_fields = (
        "cliente_nombre",
        "comentario",
        "servicio__nombre",
        "cliente__email",
    )

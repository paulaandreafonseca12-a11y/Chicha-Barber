from django.contrib import admin

from reservas.models import Reserva, Agenda


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    search_fields = (
        "nombre_usuario",
        "correo_usuario",
        "telefono_usuario",
        "observacion",
        "usuario__email",
        "servicio__nombre",
    )


@admin.register(Agenda)
class AgendaAdmin(admin.ModelAdmin):
    search_fields = (
        "profesional__email",
        "profesional__primer_nombre",
        "profesional__primer_apellido",
        "estado",
    )

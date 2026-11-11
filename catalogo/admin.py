from django.contrib import admin
from .models import Promocion


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    search_fields = (
        "nombre",
        "descripcion",
        "codigo_producto__nombre",
        "codigo_producto__codigo",
        "codigo_servicio__nombre",
    )

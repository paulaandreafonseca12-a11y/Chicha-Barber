from django.contrib import admin

from .models import (
    Venta,
    DetalleVenta,
    DetallePagos,
)


# ==========================================================
# DETALLE DE VENTA INLINE
# ==========================================================

class DetalleVentaInline(admin.TabularInline):

    model = DetalleVenta

    extra = 0


# ==========================================================
# ADMINISTRACIÓN DE VENTAS
# ==========================================================

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):

    list_display = [
        'codigo_venta',
        'nombre_cliente',
        'correo',
        'telefono',
        'metodo_pago',
        'estado_pago',
        'total_venta',
        'fecha',
    ]

    list_filter = [
        'metodo_pago',
        'estado_pago',
        'fecha',
    ]

    search_fields = [
        'nombre_cliente',
        'correo',
        'telefono',
    ]

    readonly_fields = [
        'codigo_venta',
        'total_venta',
        'fecha',
    ]

    ordering = [
        '-fecha',
    ]

    inlines = [
        DetalleVentaInline,
    ]


# ==========================================================
# ADMINISTRACIÓN DE DETALLES DE VENTA
# ==========================================================

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):

    list_display = [
        'codigo_detalle',
        'codigo_venta',
        'codigo_producto',
        'cantidad',
        'valor_descuento',
        'subtotal',
    ]

    list_filter = [
        'codigo_producto',
    ]

    search_fields = [
        'codigo_producto__nombre',
        'codigo_producto__codigo',
    ]

    readonly_fields = [
        'codigo_detalle',
        'subtotal',
    ]


# ==========================================================
# ADMINISTRACIÓN DE DATOS DE TRANSFERENCIA
# ==========================================================

@admin.register(DetallePagos)
class DetallePagosAdmin(admin.ModelAdmin):

    list_display = [
        'codigo_detalle_pago',
        'banco',
        'tipo_cuenta',
        'numero_cuenta',
        'titular',
    ]

    search_fields = [
        'banco',
        'tipo_cuenta',
        'numero_cuenta',
        'titular',
    ]

    fields = [
        'banco',
        'tipo_cuenta',
        'numero_cuenta',
        'titular',
        'instrucciones',
    ]
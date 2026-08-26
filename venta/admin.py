from django.contrib import admin
from .models import Venta, DetalleVenta, DatosTransferencia

class DetalleVentaInline(admin.TabularInline):
    model = DetalleVenta
    extra = 0

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['codigo_venta', 'nombre_cliente', 'correo', 'telefono', 'metodo_pago', 'estado_pago', 'total_compra', 'fecha']
    list_filter = ['metodo_pago', 'estado_pago', 'fecha']
    search_fields = ['nombre_cliente', 'correo', 'telefono']
    inlines = [DetalleVentaInline]

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['codigo_detalle', 'codigo_venta', 'codigo_producto', 'cantidad', 'valor_descuento', 'subtotal']

@admin.register(DatosTransferencia)
class DatosTransferenciaAdmin(admin.ModelAdmin):
    list_display = ['banco', 'tipo_cuenta', 'numero_cuenta', 'titular']

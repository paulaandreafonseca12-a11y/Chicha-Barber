from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction

from catalogo.models import Proveedor, Producto, DetalleProducto
from .models import Compra, DetalleCompra


# ==========================================================
# 📥 LISTA DE ADQUISICIONES / COMPRAS
# ==========================================================

@login_required
def lista_adquisiciones(request):
    adquisiciones = DetalleCompra.objects.select_related(
        'codigo_compra__codigo_proveedor',
        'codigo_producto__codigo_categoria'
    ).order_by('-codigo')

    total_adquisiciones = adquisiciones.count()
    total_unidades = sum(d.cantidad for d in adquisiciones)
    valor_total = sum(d.subtotal for d in adquisiciones)

    context = {
        'titulo': 'Compras',
        'adquisiciones': adquisiciones,
        'total_adquisicion': total_adquisiciones,
        'total_unidades': total_unidades,
        'valor_total': valor_total,
    }

    return render(
        request,
        'compra/compras/compra.html',
        context
    )


# ==========================================================
# ➕ REGISTRAR Compras
# ==========================================================

@login_required
def registrar_adquisicion(request):
    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor_id')
        producto_id = request.POST.get('producto_id')

        try:
            cantidad = int(request.POST.get('cantidad', '1'))
            precio_compra = Decimal(str(request.POST.get('precio_compra', '0')).replace(',', '.'))
            precio_venta_input = request.POST.get('precio_venta')
            precio_venta = Decimal(str(precio_venta_input).replace(',', '.')) if precio_venta_input else Decimal('0')
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, 'Los datos numéricos ingresados no son válidos.')
            return redirect('registrar_adquisicion')

        if cantidad <= 0:
            messages.error(request, 'La cantidad debe ser mayor que cero.')
            return redirect('registrar_adquisicion')

        if precio_compra < 0 or precio_venta < 0:
            messages.error(request, 'Los precios no pueden ser negativos.')
            return redirect('registrar_adquisicion')

        proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
        producto = get_object_or_404(Producto, codigo_producto=producto_id)

        with transaction.atomic():
            compra_obj = Compra.objects.create(
                codigo_proveedor=proveedor,
                observaciones=f"Compras para {producto.nombre}"
            )

            if precio_venta > 0:
                producto.precio = precio_venta
                producto.save(update_fields=['precio'])

            DetalleCompra.objects.create(
                codigo_compra=compra_obj,
                codigo_producto=producto,
                cantidad=cantidad,
                precio_compra=precio_compra,
                precio_venta=precio_venta if precio_venta > 0 else precio_compra
            )

        messages.success(request, f"Compras #{compra_obj.codigo} registrada con éxito.")
        return redirect('lista_adquisiciones')

    proveedores = Proveedor.objects.all().order_by('nombre')
    productos = Producto.objects.filter(estado=True).order_by('nombre')

    return render(
        request,
        'compra/compras/crear_compra.html',
        {
            'titulo': 'Registrar Compra',
            'proveedores': proveedores,
            'productos': productos,
        }
    )


# ==========================================================
# ✏️ EDITAR Compras
# ==========================================================

@login_required
def editar_adquisicion(request, pk):
    detalle = get_object_or_404(DetalleCompra, pk=pk)

    if request.method == 'POST':
        proveedor_id = request.POST.get('proveedor_id')
        producto_id = request.POST.get('producto_id')

        try:
            nueva_cantidad = int(request.POST.get('cantidad', '1'))
            nuevo_precio_compra = Decimal(str(request.POST.get('precio_compra', '0')).replace(',', '.'))
            nuevo_precio_venta_input = request.POST.get('precio_venta')
            nuevo_precio_venta = Decimal(str(nuevo_precio_venta_input).replace(',', '.')) if nuevo_precio_venta_input else Decimal('0')
        except (ValueError, TypeError, InvalidOperation):
            messages.error(request, 'Los datos numéricos ingresados no son válidos.')
            return redirect('editar_adquisicion', pk=pk)

        if nueva_cantidad <= 0 or nuevo_precio_compra < 0 or nuevo_precio_venta < 0:
            messages.error(request, 'Los valores ingresados no son válidos.')
            return redirect('editar_adquisicion', pk=pk)

        proveedor = get_object_or_404(Proveedor, pk=proveedor_id)
        producto = get_object_or_404(Producto, codigo_producto=producto_id)

        diferencia = nueva_cantidad - detalle.cantidad
        detalle_prod, _ = DetalleProducto.objects.get_or_create(codigo_producto=producto)

        with transaction.atomic():
            if diferencia < 0 and detalle_prod.cantidad_actual < abs(diferencia):
                messages.error(
                    request,
                    f"No hay suficiente existencias para reducir esta Compras. Disponible: {detalle_prod.cantidad_actual}"
                )
                return redirect('editar_adquisicion', pk=pk)

            detalle_prod.cantidad_actual += diferencia
            detalle_prod.save(update_fields=['cantidad_actual', 'fecha_actualizacion'])

            detalle.codigo_compra.codigo_proveedor = proveedor
            detalle.codigo_compra.save(update_fields=['codigo_proveedor'])

            detalle.codigo_producto = producto
            detalle.cantidad = nueva_cantidad
            detalle.precio_compra = nuevo_precio_compra
            detalle.precio_venta = nuevo_precio_venta
            detalle.subtotal = nueva_cantidad * nuevo_precio_compra
            detalle.save()

            if nuevo_precio_venta > 0:
                producto.precio = nuevo_precio_venta
                producto.save(update_fields=['precio'])

            detalle.codigo_compra.actualizar_total()

        messages.success(request, 'Compras actualizada correctamente.')
        return redirect('lista_adquisiciones')

    proveedores = Proveedor.objects.all().order_by('nombre')
    productos = Producto.objects.all().order_by('nombre')

    return render(
        request,
        'compra/compras/editar_compra.html',
        {
            'titulo': 'Editar Compras',
            'adquisicion': detalle,
            'proveedores': proveedores,
            'productos': productos,
        }
    )


# ==========================================================
# 🗑️ ELIMINAR Compras
# ==========================================================

@login_required
def eliminar_adquisicion(request, pk):
    detalle = get_object_or_404(DetalleCompra, pk=pk)
    compra = detalle.codigo_compra
    detalle_prod, _ = DetalleProducto.objects.get_or_create(codigo_producto=detalle.codigo_producto)

    if detalle_prod.cantidad_actual < detalle.cantidad:
        messages.error(
            request,
            f"No se puede eliminar la Compras porque el stock actual ({detalle_prod.cantidad_actual}) es menor que la cantidad adquirida ({detalle.cantidad})."
        )
        return redirect('lista_adquisiciones')

    with transaction.atomic():
        detalle_prod.cantidad_actual -= detalle.cantidad
        detalle_prod.save(update_fields=['cantidad_actual', 'fecha_actualizacion'])

        if detalle.codigo_movimiento_producto:
            detalle.codigo_movimiento_producto.delete()

        detalle.delete()

        if compra.detalles.count() == 0:
            compra.delete()
        else:
            compra.actualizar_total()

    messages.success(request, 'Compras eliminada correctamente.')
    return redirect('lista_adquisiciones')

from decimal import Decimal, InvalidOperation
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction

from catalogo.models import Producto
from .models import Venta, DetalleVenta, DatosTransferencia
from .forms import VentaForm, DetalleVentaForm, DatosTransferenciaForm

try:
    from core.utils import enviar_correo_venta
except ImportError:
    enviar_correo_venta = None


# ==========================================================
# 🛒 CLIENTE - CARRITO
# ==========================================================

def carrito(request):
    return render(
        request,
        'venta/carrito/Carrito.html'
    )


def agregar_carrito(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)

    id_producto = request.POST.get('id')
    nombre = request.POST.get('nombre', '')
    precio = request.POST.get('precio', '0')

    if not id_producto:
        return JsonResponse({'ok': False, 'error': 'ID no proporcionado'}, status=400)

    carrito_session = request.session.get('carrito', {})

    if str(id_producto) in carrito_session:
        carrito_session[str(id_producto)]['cantidad'] += 1
    else:
        carrito_session[str(id_producto)] = {
            'nombre': nombre,
            'precio': float(precio),
            'cantidad': 1
        }

    request.session['carrito'] = carrito_session
    request.session.modified = True

    return JsonResponse({'ok': True})


# ==========================================================
# 💳 CLIENTE - PAGO & CHECKOUT
# ==========================================================

def pago(request):
    factura_id = request.GET.get('factura_id')
    if factura_id:
        request.session['active_factura_id'] = factura_id

    context = {
        'titulo': 'Método de Pago',
        'datos_banco': DatosTransferencia.get_solo(),
        'factura_id': request.session.get('active_factura_id'),
    }

    return render(
        request,
        'venta/pagos/pago.html',
        context
    )


def procesar_pago_cliente(request):
    if request.method != 'POST':
        return redirect('carrito')

    nombre = request.POST.get('nombre', '').strip()
    correo = request.POST.get('correo', '').strip()
    telefono = request.POST.get('telefono', '').strip()
    metodo_pago_raw = request.POST.get('pago', 'efectivo')
    tipo_transferencia = request.POST.get('tipo_transferencia', '')
    carrito_json = request.POST.get('carrito', '[]')
    comprobante_archivo = request.FILES.get('comprobante')

    if not carrito_json or carrito_json == '[]':
        messages.error(request, 'El carrito está vacío.')
        return redirect('carrito')

    try:
        carrito_data = json.loads(carrito_json)
    except (json.JSONDecodeError, TypeError):
        messages.error(request, 'Formato del carrito no válido.')
        return redirect('carrito')

    if not carrito_data:
        messages.error(request, 'El carrito no contiene elementos.')
        return redirect('carrito')

    # Mapeo de método de pago para el modelo
    if metodo_pago_raw in ['transferencia', 'daviplata', 'nequi']:
        metodo_pago = 'transferencia'
        estado_pago = 'pendiente'
    else:
        metodo_pago = 'efectivo'
        estado_pago = 'completado'

    user = request.user if request.user.is_authenticated else None

    try:
        with transaction.atomic():
            nueva_venta = Venta.objects.create(
                codigo_usuario=user,
                nombre_cliente=nombre,
                correo=correo,
                telefono=telefono,
                metodo_pago=metodo_pago,
                estado_pago=estado_pago,
                total_compra=0
            )

            total_general = Decimal('0')

            for item in carrito_data:
                if item.get('tipo') == 'reserva':
                    # Elementos tipo reserva
                    precio_reserva = Decimal(str(item.get('precio', 0)))
                    total_general += precio_reserva
                    continue

                producto_id = item.get('id')
                cantidad = int(item.get('cantidad', 1))

                if cantidad <= 0:
                    raise ValueError('La cantidad de cada producto debe ser mayor a cero.')

                producto = get_object_or_404(Producto, codigo_producto=producto_id)

                detalle = DetalleVenta.objects.create(
                    codigo_venta=nueva_venta,
                    codigo_producto=producto,
                    cantidad=cantidad,
                    valor_descuento=Decimal('0')
                )

                total_general += detalle.subtotal

            nueva_venta.total_compra = total_general
            nueva_venta.save(update_fields=['total_compra'])

            # Limpiar sesión del carrito
            if 'carrito' in request.session:
                request.session['carrito'] = {}
                request.session.modified = True

    except ValueError as e:
        messages.error(request, str(e))
        return redirect('pago')
    except Exception as e:
        messages.error(request, f"Error al procesar la venta: {str(e)}")
        return redirect('pago')

    # Intentar enviar correo de confirmación
    if enviar_correo_venta and correo:
        try:
            enviar_correo_venta(
                correo_cliente=correo,
                nombre=nombre,
                carrito=carrito_data,
                total=float(total_general)
            )
        except Exception:
            pass

    if metodo_pago == 'transferencia':
        messages.success(request, f"¡Venta #{nueva_venta.codigo_venta} registrada! El comprobante será verificado por el administrador.")
    else:
        messages.success(request, f"¡Venta #{nueva_venta.codigo_venta} completada con éxito!")

    return redirect('productos_galeria')


# ==========================================================
# 📊 VENTAS ADMIN - HISTORIAL & GESTIÓN
# ==========================================================

@login_required
def historial_ventas(request):
    ventas = Venta.objects.all().order_by('-fecha')
    total_ventas = ventas.count()

    context = {
        'titulo': 'Historial de Ventas',
        'ventas': ventas,
        'total_ventas': total_ventas,
    }

    return render(
        request,
        'venta/ventas/ventas.html',
        context
    )


@login_required
def registrar_venta(request):
    if request.method == 'POST':
        form_venta = VentaForm(request.POST)
        form_detalle = DetalleVentaForm(request.POST)

        if form_venta.is_valid() and form_detalle.is_valid():
            try:
                with transaction.atomic():
                    nueva_venta = form_venta.save()
                    detalle = form_detalle.save(commit=False)
                    detalle.codigo_venta = nueva_venta
                    detalle.save()
                    nueva_venta.actualizar_total()

                messages.success(request, f"Venta #{nueva_venta.codigo_venta} registrada exitosamente.")
                return redirect('historial_ventas')
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f"Error al registrar la venta: {str(e)}")
    else:
        form_venta = VentaForm()
        form_detalle = DetalleVentaForm()

    context = {
        'titulo': 'Registrar Nueva Venta',
        'form_venta': form_venta,
        'form_detalle': form_detalle,
    }

    return render(
        request,
        'compra/compras/registrar_compra.html',
        context
    )


@login_required
def detalle_venta(request, pk):
    venta_obj = get_object_or_404(Venta, codigo_venta=pk)
    detalles = venta_obj.detalles.select_related('codigo_producto').all()

    context = {
        'titulo': f'Detalle de Venta #{venta_obj.codigo_venta}',
        'venta': venta_obj,
        'detalles': detalles,
        'total_calculado': venta_obj.total_compra,
    }

    return render(
        request,
        'venta/ventas/detalle_venta.html',
        context
    )


@login_required
def eliminar_venta(request, pk):
    venta_obj = get_object_or_404(Venta, codigo_venta=pk)

    if request.method == 'POST':
        venta_obj.delete()
        messages.success(request, f"Venta #{pk} eliminada exitosamente.")

    return redirect('historial_ventas')


# ==========================================================
# 🏦 DATOS BANCARIOS (ADMIN)
# ==========================================================

@login_required
def ver_datos_banco(request):
    return render(
        request,
        'venta/detalles_pagos/ver_datos_banco.html',
        {
            'titulo': 'Datos Bancarios',
            'datos': DatosTransferencia.get_solo(),
        }
    )


@login_required
def editar_datos_banco(request):
    if not request.user.is_staff and getattr(request.user, 'rol', '') != 'admin':
        messages.error(request, 'No tienes permisos para editar los datos bancarios.')
        return redirect('inicio')

    datos = DatosTransferencia.get_solo()

    if request.method == 'POST':
        form = DatosTransferenciaForm(request.POST, instance=datos)
        if form.is_valid():
            form.save()
            messages.success(request, 'Datos bancarios actualizados correctamente.')
            return redirect('ver_datos_banco')
    else:
        form = DatosTransferenciaForm(instance=datos)

    return render(
        request,
        'venta/detalles_pagos/editar_datos_banco.html',
        {
            'titulo': 'Editar Datos Bancarios',
            'datos': datos,
            'form': form,
        }
    )

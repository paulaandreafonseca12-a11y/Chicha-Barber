from decimal import Decimal
import json

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction

from catalogo.models import Producto

from .models import (
    Venta,
    DetalleVenta,
    DetallePagos,
)

from .forms import (
    VentaForm,
    DetalleVentaForm,
    DetallePagosForm,
)


# ==========================================================
# ENVÍO DE CORREO
# ==========================================================

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

        return JsonResponse(
            {
                'ok': False,
                'error': 'Método no permitido'
            },
            status=405
        )

    id_producto = request.POST.get('id')
    nombre = request.POST.get(
        'nombre',
        ''
    )
    precio = request.POST.get(
        'precio',
        '0'
    )

    if not id_producto:

        return JsonResponse(
            {
                'ok': False,
                'error': 'ID no proporcionado'
            },
            status=400
        )

    carrito_session = request.session.get(
        'carrito',
        {}
    )

    if str(id_producto) in carrito_session:

        carrito_session[
            str(id_producto)
        ]['cantidad'] += 1

    else:

        carrito_session[
            str(id_producto)
        ] = {

            'nombre': nombre,

            'precio': float(
                precio
            ),

            'cantidad': 1
        }

    request.session['carrito'] = (
        carrito_session
    )

    request.session.modified = True

    return JsonResponse(
        {
            'ok': True
        }
    )


# ==========================================================
# 💳 CLIENTE - PAGO
# ==========================================================

def pago(request):

    factura_id = request.GET.get(
        'factura_id'
    )

    if factura_id:

        request.session[
            'active_factura_id'
        ] = factura_id

    # ======================================================
    # OBTENER DATOS BANCARIOS
    # ======================================================
    #
    # DetallePagos ahora está asociado a una Venta.
    #
    # Para mostrar los datos bancarios generales antes
    # de crear la venta, tomamos el primer registro existente.
    #
    # Esto NO se utiliza para crear el pago de una venta.
    #
    # ======================================================

    datos_banco = (
        DetallePagos.objects.first()
    )

    context = {

        'titulo': 'Método de Pago',

        'datos_banco': datos_banco,

        'factura_id': request.session.get(
            'active_factura_id'
        ),
    }

    return render(
        request,
        'venta/pagos/pago.html',
        context
    )


# ==========================================================
# 💳 PROCESAR PAGO DEL CLIENTE
# ==========================================================

def procesar_pago_cliente(request):

    if request.method != 'POST':

        return redirect(
            'carrito'
        )

    # ======================================================
    # DATOS DEL CLIENTE
    # ======================================================

    nombre = request.POST.get(
        'nombre',
        ''
    ).strip()

    correo = request.POST.get(
        'correo',
        ''
    ).strip()

    telefono = request.POST.get(
        'telefono',
        ''
    ).strip()

    metodo_pago_raw = request.POST.get(
        'pago',
        'efectivo'
    )

    tipo_transferencia = request.POST.get(
        'tipo_transferencia',
        ''
    )

    carrito_json = request.POST.get(
        'carrito',
        '[]'
    )

    comprobante_archivo = (
        request.FILES.get(
            'comprobante'
        )
    )

    # ======================================================
    # VALIDAR CARRITO
    # ======================================================

    if (
        not carrito_json
        or carrito_json == '[]'
    ):

        messages.error(
            request,
            'El carrito está vacío.'
        )

        return redirect(
            'carrito'
        )

    try:

        carrito_data = json.loads(
            carrito_json
        )

    except (
        json.JSONDecodeError,
        TypeError
    ):

        messages.error(
            request,
            'Formato del carrito no válido.'
        )

        return redirect(
            'carrito'
        )

    if not carrito_data:

        messages.error(
            request,
            'El carrito no contiene elementos.'
        )

        return redirect(
            'carrito'
        )

    # ======================================================
    # DETERMINAR MÉTODO DE PAGO
    # ======================================================

    if metodo_pago_raw in [
        'transferencia',
        'daviplata',
        'nequi'
    ]:

        metodo_pago = 'transferencia'

        estado_pago = 'pendiente'

    else:

        metodo_pago = 'efectivo'

        estado_pago = 'completado'

    # ======================================================
    # USUARIO
    # ======================================================

    user = (
        request.user
        if request.user.is_authenticated
        else None
    )

    try:

        with transaction.atomic():

            # ==================================================
            # CREAR VENTA
            # ==================================================

            nueva_venta = Venta.objects.create(

                codigo_usuario=user,

                nombre_cliente=nombre,

                correo=correo,

                telefono=telefono,

                metodo_pago=metodo_pago,

                estado_pago=estado_pago,

                total_venta=Decimal('0')
            )

            total_general = Decimal('0')

            # ==================================================
            # PROCESAR CARRITO
            # ==================================================

            for item in carrito_data:

                # ==============================================
                # RESERVA
                # ==============================================

                if item.get(
                    'tipo'
                ) == 'reserva':

                    precio_reserva = Decimal(
                        str(
                            item.get(
                                'precio',
                                0
                            )
                        )
                    )

                    total_general += (
                        precio_reserva
                    )

                    continue

                # ==============================================
                # PRODUCTO
                # ==============================================

                producto_id = item.get(
                    'id'
                )

                cantidad = int(
                    item.get(
                        'cantidad',
                        1
                    )
                )

                if cantidad <= 0:

                    raise ValueError(
                        'La cantidad de cada '
                        'producto debe ser mayor '
                        'a cero.'
                    )

                producto = get_object_or_404(
                    Producto,
                    codigo_producto=producto_id
                )

                # ==============================================
                # CREAR DETALLE
                # ==============================================

                detalle = (
                    DetalleVenta.objects.create(

                        codigo_venta=nueva_venta,

                        codigo_producto=producto,

                        cantidad=cantidad,

                        valor_descuento=Decimal('0')
                    )
                )

                total_general += (
                    detalle.subtotal
                )

            # ==================================================
            # ACTUALIZAR TOTAL
            # ==================================================

            nueva_venta.total_venta = (
                total_general
            )

            nueva_venta.save(
                update_fields=[
                    'total_venta'
                ]
            )

            # ==================================================
            # CREAR DETALLE DE PAGO
            # ==================================================
            #
            # IMPORTANTE:
            #
            # Ya NO utilizamos:
            #
            #     get_or_create(pk=1)
            #
            # Cada pago se relaciona con la venta actual.
            #
            # ==================================================

            if metodo_pago == 'transferencia':

                DetallePagos.get_or_create_para_venta(

                    nueva_venta,

                    banco=request.POST.get(
                        'banco',
                        'Bancolombia'
                    ),

                    tipo_cuenta=request.POST.get(
                        'tipo_cuenta',
                        'Ahorros'
                    ),

                    numero_cuenta=request.POST.get(
                        'numero_cuenta',
                        '123-456789-01'
                    ),

                    titular=request.POST.get(
                        'titular',
                        'Chicha Barber Studio SAS'
                    ),

                    instrucciones=request.POST.get(
                        'instrucciones',
                        'Comprobante registrado '
                        'en proceso de verificación.'
                    )
                )

            # ==================================================
            # LIMPIAR CARRITO
            # ==================================================

            if 'carrito' in request.session:

                request.session[
                    'carrito'
                ] = {}

                request.session.modified = True

    # ======================================================
    # ERRORES
    # ======================================================

    except ValueError as e:

        messages.error(
            request,
            str(e)
        )

        return redirect(
            'pago'
        )

    except Exception as e:

        messages.error(
            request,
            f'Error al procesar la venta: {str(e)}'
        )

        return redirect(
            'pago'
        )

    # ======================================================
    # ENVIAR CORREO
    # ======================================================

    if (
        enviar_correo_venta
        and correo
    ):

        try:

            enviar_correo_venta(

                correo_cliente=correo,

                nombre=nombre,

                carrito=carrito_data,

                total=float(
                    total_general
                )
            )

        except Exception:

            pass

    # ======================================================
    # MENSAJE FINAL
    # ======================================================

    if metodo_pago == 'transferencia':

        messages.success(
            request,
            (
                f'¡Venta #{nueva_venta.codigo_venta} '
                'registrada! El comprobante será '
                'verificado por el administrador.'
            )
        )

    else:

        messages.success(
            request,
            (
                f'¡Venta #{nueva_venta.codigo_venta} '
                'completada con éxito!'
            )
        )

    return redirect(
        'productos_galeria'
    )


# ==========================================================
# 📊 VENTAS ADMIN - HISTORIAL
# ==========================================================

@login_required
def historial_ventas(request):

    ventas = (
        Venta.objects
        .all()
        .order_by('-fecha')
    )

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


# ==========================================================
# 📝 REGISTRAR VENTA MANUALMENTE
# ==========================================================

@login_required
def registrar_venta(request):

    if request.method == 'POST':

        form_venta = VentaForm(
            request.POST
        )

        form_detalle = DetalleVentaForm(
            request.POST
        )

        if (
            form_venta.is_valid()
            and form_detalle.is_valid()
        ):

            try:

                with transaction.atomic():

                    # ==========================================
                    # CREAR VENTA
                    # ==========================================

                    nueva_venta = (
                        form_venta.save()
                    )

                    # ==========================================
                    # CREAR DETALLE
                    # ==========================================

                    detalle = (
                        form_detalle.save(
                            commit=False
                        )
                    )

                    detalle.codigo_venta = (
                        nueva_venta
                    )

                    detalle.save()

                    # ==========================================
                    # ACTUALIZAR TOTAL
                    # ==========================================

                    nueva_venta.actualizar_total()

                    # ==========================================
                    # CREAR DETALLE DE PAGO SI ES
                    # TRANSFERENCIA
                    # ==========================================

                    if (
                        nueva_venta.metodo_pago
                        == 'transferencia'
                    ):

                        DetallePagos.get_or_create_para_venta(
                            nueva_venta
                        )

                messages.success(
                    request,
                    (
                        f'Venta #{nueva_venta.codigo_venta} '
                        'registrada exitosamente.'
                    )
                )

                return redirect(
                    'historial_ventas'
                )

            except ValueError as e:

                messages.error(
                    request,
                    str(e)
                )

            except Exception as e:

                messages.error(
                    request,
                    (
                        'Error al registrar la venta: '
                        f'{str(e)}'
                    )
                )

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


# ==========================================================
# 🔎 DETALLE DE VENTA
# ==========================================================

@login_required
def detalle_venta(request, pk):

    venta_obj = get_object_or_404(
        Venta,
        codigo_venta=pk
    )

    detalles = (
        venta_obj.detalles
        .select_related(
            'codigo_producto'
        )
        .all()
    )

    context = {

        'titulo': (
            f'Detalle de Venta '
            f'#{venta_obj.codigo_venta}'
        ),

        'venta': venta_obj,

        'detalles': detalles,

        'total_calculado': (
            venta_obj.total_compra
        ),
    }

    return render(
        request,
        'venta/ventas/detalle_venta.html',
        context
    )


# ==========================================================
# 🗑️ ELIMINAR VENTA
# ==========================================================

@login_required
def eliminar_venta(request, pk):

    venta_obj = get_object_or_404(
        Venta,
        codigo_venta=pk
    )

    if request.method == 'POST':

        venta_obj.delete()

        messages.success(
            request,
            (
                f'Venta #{pk} '
                'eliminada exitosamente.'
            )
        )

    return redirect(
        'historial_ventas'
    )


# ==========================================================
# 🏦 DATOS BANCARIOS - ADMIN
# ==========================================================

@login_required
def ver_datos_banco(request):

    datos = (
        DetallePagos.objects
        .order_by(
            'codigo_detalle_pago'
        )
        .first()
    )

    return render(
        request,
        'venta/detalles_pagos/ver_datos_banco.html',
        {
            'titulo': 'Datos Bancarios',
            'datos': datos,
        }
    )


# ==========================================================
# ✏️ EDITAR DATOS BANCARIOS - ADMIN
# ==========================================================

@login_required
def editar_datos_banco(request):

    if (
        not request.user.is_staff
        and getattr(
            request.user,
            'rol',
            ''
        ) != 'admin'
    ):

        messages.error(
            request,
            (
                'No tienes permisos para '
                'editar los datos bancarios.'
            )
        )

        return redirect(
            'inicio'
        )

    datos = (
        DetallePagos.objects
        .order_by(
            'codigo_detalle_pago'
        )
        .first()
    )

    # ======================================================
    # SI NO EXISTE NINGÚN DETALLE DE PAGO
    # ======================================================

    if not datos:

        messages.warning(
            request,
            (
                'Aún no existen datos bancarios '
                'asociados a una venta.'
            )
        )

        return redirect(
            'historial_ventas'
        )

    # ======================================================
    # PROCESAR FORMULARIO
    # ======================================================

    if request.method == 'POST':

        form = DetallePagosForm(
            request.POST,
            instance=datos
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                (
                    'Datos bancarios actualizados '
                    'correctamente.'
                )
            )

            return redirect(
                'ver_datos_banco'
            )

    else:

        form = DetallePagosForm(
            instance=datos
        )

    return render(
        request,
        'venta/detalles_pagos/editar_datos_banco.html',
        {
            'titulo': 'Editar Datos Bancarios',

            'datos': datos,

            'form': form,
        }
    )


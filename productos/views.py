
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Compra, Producto, DetalleCompra, Stock, DatosTransferencia
from .forms import CompraForm, DetalleCompraForm, ProductoForm, StockForm 
from django.http import JsonResponse
import json
from django.db import transaction
from django.db.models import Sum
from core.utils import enviar_correo_compra
from facturas.models import Factura, DetalleFactura


# ==========================================
# 🟢 CLIENTE (Vistas de la Tienda)
# ==========================================

def productos_galeria(request):
    factura_id = request.GET.get('factura_id')

    if factura_id:
        request.session['active_factura_id'] = factura_id

    context = {
        'titulo': 'Galería de Productos',
        'productos': Producto.objects.filter(estado=True)
    }

    return render(request, 'productos/productos_galeria.html', context)

# 🔒 CARRITO PROTEGIDO
@login_required
def carrito(request):
    return render(request, 'productos/carrito.html')


# 🔒 PAGO PROTEGIDO
@login_required
def pago(request):
    context = {
        'titulo': 'Método de Pago',
        'datos_banco': DatosTransferencia.get_solo(),
        'factura_id': request.session.get('active_factura_id')
    }

    return render(request, 'productos/pago.html', context)


# 🔒 PROCESAR PAGO PROTEGIDO (CORREGIDO Y OPTIMIZADO)
@login_required
def procesar_pago_cliente(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        metodo_pago = request.POST.get('pago')  # Recibe 'persona', 'contraentrega' o 'transferencia'
        tipo_transferencia = request.POST.get('tipo_transferencia') # 'nequi', 'daviplata'
        factura_id = request.POST.get('factura_id')
        carrito_json = request.POST.get('carrito')
        
        # 📸 Capturar el archivo del comprobante adjunto
        comprobante_archivo = request.FILES.get('comprobante')

        # 🔴 Validar carrito
        if not carrito_json:
            messages.error(request, "❌ El carrito está vacío")
            return redirect('carrito')

        try:
            carrito_data = json.loads(carrito_json)
        except (json.JSONDecodeError, TypeError):
            messages.error(request, "❌ Error en el formato del carrito")
            return redirect('carrito')

        if not carrito_data:
            messages.error(request, "❌ El carrito no contiene elementos")
            return redirect('carrito')

        # 🔴 Validación crítica: Si elige transferencia, el comprobante es obligatorio
        if metodo_pago in ['transferencia', 'contraentrega'] and not comprobante_archivo:
            messages.error(request, "❌ Adjuntar el comprobante es obligatorio para este método de pago.")
            return redirect('pago')

        try:
            # 🛡️ Garantiza la consistencia: si el stock falla en algún ítem, se revierte todo
            with transaction.atomic():
                
                # 🏦 Todo pago (persona, contraentrega o transferencia) requiere verificación manual del admin
                estado_inicial = 'pendiente_verificacion'

                # ✅ Mapeo para que la Factura tenga el método exacto (Nequi, Daviplata, etc.)
                metodo_factura = 'efectivo'
                if metodo_pago in ['transferencia', 'contraentrega'] and tipo_transferencia:
                    metodo_factura = tipo_transferencia

                # ✅ 1. Obtener o crear cabecera de Factura
                if factura_id:
                    factura = get_object_or_404(Factura, id=factura_id)
                else:
                    estado_factura = 'pagada' if estado_inicial == 'completado' else 'pendiente'
                    factura = Factura.objects.create(
                        cliente=request.user,
                        metodo_pago=metodo_factura,
                        total_pagado=0,
                        estado=estado_factura,
                        imagen_transaccion=comprobante_archivo
                    )

                # ✅ 2. Crear cabecera única de Compra para gestión logística/inventario
                compra = Compra.objects.create(
                    usuario=request.user,
                    nombre_cliente=nombre,
                    correo=correo,
                    telefono=telefono,
                    metodo_pago=metodo_pago,
                    estado_pago=estado_inicial,
                    comprobante=comprobante_archivo,
                    total=0  # Se actualizará al final
                )

                total_general = 0

                # ✅ 3. Iterar los productos y generar sus registros detallados hijos
                for item in carrito_data:
                    producto = get_object_or_404(Producto, codigo_producto=item['id'])
                    cantidad = int(item['cantidad'])

                    # Al invocar el .create(), se ejecuta la lógica del nuevo save() del modelo:
                    # Calcula subtotal, valida stock, reduce stock y guarda el movimiento logístico.
                    detalle_compra_obj = DetalleCompra.objects.create(
                        compra=compra,
                        producto=producto,
                        cantidad=cantidad
                    )

                    # Registramos el detalle correspondiente en la Factura del cliente
                    DetalleFactura.objects.create(
                        factura=factura,
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=producto.precio_venta,
                        subtotal=detalle_compra_obj.subtotal
                    )

                    total_general += detalle_compra_obj.subtotal

                # ✅ 4. Actualización limpia de totales una única vez
                compra.total = total_general
                compra.save(update_fields=['total'])

                factura.total_pagado = float(total_general)
                factura.save(update_fields=['total_pagado'])

                # Limpiar factura activa
                if 'active_factura_id' in request.session:
                    del request.session['active_factura_id']

                # Vaciamos de forma limpia el backend de la sesión
                request.session['carrito'] = {}
                request.session.modified = True

        except ValueError as e:
            # Captura el error controlado de "Stock insuficiente" enviado por el save() del modelo
            messages.error(request, f"❌ Operación cancelada: {str(e)}")
            return redirect('carrito')
        except Exception as e:
            messages.error(request, f"❌ Error crítico en la transacción: {str(e)}")
            return redirect('carrito')

        # ✅ Enviar correo de confirmación
        try:
            enviar_correo_compra(
                correo_cliente=correo,
                nombre=nombre,
                carrito=carrito_data,
                total=total_general
            )
        except Exception as e:
            print(f"Error enviando correo: {e}")

        # Mensaje de éxito según método
        if metodo_pago in ['transferencia', 'contraentrega']:
            messages.success(
                request, 
                "✅ Orden registrada. El administrador verificará tu comprobante de transferencia a la brevedad."
            )
        else:
            messages.success(request, "✅ Compra realizada con éxito")

        return redirect('facturas')

    return redirect('carrito')


# ==========================================
# 🔵 ADMIN PRODUCTOS
# ==========================================

def lista_productos_admin(request):
    productos = Producto.objects.all()

    context = {
        'titulo': 'Lista de Productos',
        'productos': productos,
        'total_productos': Producto.total_productos(),
        'activos': Producto.total_activos(),
        'inactivos': Producto.total_inactivos(),
    }

    return render(request, 'productos/productos_admin.html', context)

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto creado correctamente")
            return redirect('lista_productos_admin')

    else:
        form = ProductoForm()

    context = {
        'titulo': 'Crear Producto',
        'form': form
    }

    return render(request, 'productos/crear_producto.html', context)


def editar_producto(request, pk):
    producto = get_object_or_404(Producto, codigo_producto=pk)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)

        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto actualizado correctamente")
            return redirect('lista_productos_admin')

    else:
        form = ProductoForm(instance=producto)

    context = {
        'titulo': 'Editar Producto',
        'form': form,
        'producto': producto
    }

    return render(request, 'productos/editar_producto.html', context)


def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, codigo_producto=pk)
    producto.delete()
    messages.success(request, "✅ Producto eliminado correctamente")
    return redirect('lista_productos_admin')


# ==========================================
# 🔥 STOCK (Inventario)
# ==========================================

def lista_stock(request):
    stocks = Stock.objects.select_related('producto')

    stock_total = stocks.aggregate(total=Sum('cantidad'))['total'] or 0
    valor_stock = sum((stock.cantidad or 0) * (stock.producto.precio_venta or 0) for stock in stocks)

    context = {
        'titulo': 'Stock de Productos',
        'stocks': stocks,
        'total_productos': stocks.count(),
        'stock_total': stock_total,
        'stock_critico': stocks.filter(cantidad__lte=5).count(),
        'stock_bajo': stocks.filter(cantidad__gt=5, cantidad__lte=10).count(),
        'stock_optimo': stocks.filter(cantidad__gt=10).count(),
        'valor_stock': valor_stock,
    }

    return render(request, 'productos/stock_admin.html', context)


def editar_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)

    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)

        if form.is_valid():
            form.save()
            messages.success(request, "✅ Stock actualizado correctamente")
            return redirect('lista_stock')

    else:
        form = StockForm(instance=stock)

    context = {
        'titulo': f'Editar Stock - {stock.producto.nombre}',
        'form': form,
        'stock': stock
    }

    return render(request, 'productos/editar_stock.html', context)


# ==========================================
# 🟡 COMPRAS ADMIN (Gestión de historial)
# ==========================================

def registrar_compra(request):
    if request.method == 'POST':
        form_compra = CompraForm(request.POST)
        form_detalle = DetalleCompraForm(request.POST)

        if form_compra.is_valid() and form_detalle.is_valid():
            nueva_compra = form_compra.save()

            detalle = form_detalle.save(commit=False)
            detalle.compra = nueva_compra
            detalle.save()

            nueva_compra.total = detalle.subtotal
            nueva_compra.save(update_fields=['total'])

            messages.success(request, "✅ Compra registrada exitosamente")
            return redirect('historial_compras')

    else:
        form_compra = CompraForm()
        form_detalle = DetalleCompraForm()

    context = {
        'titulo': 'Registrar Nueva Compra',
        'form_compra': form_compra,
        'form_detalle': form_detalle
    }

    return render(request, 'productos/registrar_compra.html', context)


def historial_compras(request):
    compras = Compra.objects.all().order_by('-fecha_compra')

    context = {
        'titulo': 'Historial de Compras',
        'compras': compras,
        'total_compras': compras.count(),
    }

    return render(request, 'productos/historial_compras.html', context)

def detalle_compra(request, pk):
    compra = get_object_or_404(Compra, codigo_compra=pk)

    context = {
        'titulo': 'Detalle de Compra',
        'compra': compra,
        'detalles': compra.detalles.all(),
        'total_calculado': sum(d.subtotal for d in compra.detalles.all())
    }

    return render(request, 'productos/detalle_compra.html', context)

def eliminar_compra(request, pk):
    compra = get_object_or_404(Compra, codigo_compra=pk)
    if request.method == 'POST':
        compra.delete()
        messages.success(request, "✅ Compra eliminada")
    return redirect('historial_compras')


# ==========================================
# 🛒 MECHANISMOS INTERNOS DEL CARRITO
# ==========================================

def agregar_carrito(request):
    if request.method == 'POST':
        id_producto = request.POST.get('id')
        nombre = request.POST.get('nombre')
        precio = request.POST.get('precio')

        carrito = request.session.get('carrito', {})

        if id_producto in carrito:
            carrito[id_producto]['cantidad'] += 1
        else:
            carrito[id_producto] = {
                'nombre': nombre,
                'precio': float(precio),
                'cantidad': 1
            }

        request.session['carrito'] = carrito
        request.session.modified = True
        return JsonResponse({'ok': True})

    return JsonResponse({'ok': False})


@login_required
def editar_datos_banco(request):
    if not request.user.is_staff:
        messages.error(request, "❌ No tienes permisos.")
        return redirect('inicio')

    datos = DatosTransferencia.get_solo()

    if request.method == 'POST':
        datos.banco = request.POST.get('banco', '').strip()
        datos.tipo_cuenta = request.POST.get('tipo_cuenta', '').strip()
        datos.numero_cuenta = request.POST.get('numero_cuenta', '').strip()
        datos.titular = request.POST.get('titular', '').strip()
        datos.instrucciones = request.POST.get('instrucciones', '').strip()
        datos.save()

        messages.success(request, "✅ Datos actualizados")

    context = {
        'titulo': 'Editar Datos Bancarios',
        'datos': datos
    }

    return render(request, 'productos/editar_datos_banco.html', context)


@login_required
def ver_datos_banco(request):
    context = {
        'titulo': 'Datos Bancarios',
        'datos': DatosTransferencia.get_solo()
    }

    return render(request, 'productos/ver_datos_banco.html', context)
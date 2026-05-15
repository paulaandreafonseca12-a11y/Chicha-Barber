from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Compra, Producto, DetalleCompra, Stock
from .forms import CompraForm, DetalleCompraForm, ProductoForm, StockForm
from django.http import JsonResponse
import json
from django.db import transaction
from core.utils import enviar_correo_compra


# =========================
# 🟢 CLIENTE
# =========================

def productos_galeria(request):

    productos = Producto.objects.all()

    return render(request, 'productos/productos_galeria.html', {
        'productos': productos
    })


# 🔒 CARRITO PROTEGIDO
# Si no tiene sesión -> va a registro
def carrito(request):
    if not request.user.is_authenticated:
        login_url = reverse('registro')
        return redirect(f'{login_url}?next={request.get_full_path()}')

    return render(request, 'productos/carrito.html')


# 🔒 PAGO PROTEGIDO
def pago(request):
    if not request.user.is_authenticated:
        login_url = reverse('registro')
        return redirect(f'{login_url}?next={request.get_full_path()}')

    return render(request, 'productos/pago.html')


# 🔒 PROCESAR PAGO PROTEGIDO
def procesar_pago_cliente(request):
    if not request.user.is_authenticated:
        login_url = reverse('registro')
        return redirect(f'{login_url}?next={request.get_full_path()}')

    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        metodo_pago = request.POST.get('pago')
        carrito_json = request.POST.get('carrito')

        # 🔴 Validar carrito
        if not carrito_json:

            messages.error(
                request,
                "❌ El carrito está vacío"
            )

            return redirect('carrito')

        try:

            carrito = json.loads(carrito_json)

        except:

            messages.error(
                request,
                "❌ Error en el carrito"
            )

            return redirect('carrito')

        if not carrito:

            messages.error(
                request,
                "❌ El carrito está vacío"
            )

            return redirect('carrito')

        try:

            with transaction.atomic():

                # ✅ Crear compra
                compra = Compra.objects.create(
                    nombre_cliente=nombre,
                    correo=correo,
                    telefono=telefono,
                    direccion=direccion,
                    metodo_pago=metodo_pago,
                    total=0
                )

                total_compra = 0

                # ✅ Crear detalles
                for item in carrito:

                    producto = get_object_or_404(
                        Producto,
                        codigo_producto=item['id']
                    )

                    cantidad = int(item['cantidad'])

                    subtotal = (
                        producto.precio_venta * cantidad
                    )

                    total_compra += subtotal

                    DetalleCompra.objects.create(
                        compra=compra,
                        producto=producto,
                        cantidad=cantidad,
                        subtotal=subtotal
                    )

                # ✅ Guardar total
                compra.total = total_compra
                compra.save()

        except Exception as e:

            messages.error(
                request,
                f"❌ Error en la compra: {str(e)}"
            )

            return redirect('carrito')

        # ✅ Enviar correo
        try:

            enviar_correo_compra(
                correo_cliente=correo,
                nombre=nombre,
                carrito=carrito,
                total=total_compra
            )

        except Exception as e:

            print(f"Error enviando correo: {e}")

        messages.success(
            request,
            "✅ Compra realizada con éxito"
        )

        return redirect('pago')

    return redirect('carrito')


# =========================
# 🔵 ADMIN PRODUCTOS
# =========================

def lista_productos_admin(request):

    productos = Producto.objects.all()

    return render(request, 'productos/productos_admin.html', {
        'productos': productos,
        'titulo': "Nuestros Productos",
    })


def crear_producto(request):

    if request.method == 'POST':

        form = ProductoForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            producto = form.save()

            # 🔥 Crear stock automático
            Stock.objects.get_or_create(
                producto=producto
            )

            messages.success(
                request,
                "✅ Producto creado correctamente"
            )

            return redirect('lista_productos_admin')

        else:

            messages.error(
                request,
                "❌ Error al crear producto"
            )

    else:

        form = ProductoForm()

    return render(request, 'productos/editar_producto.html', {
        'form': form
    })


def editar_producto(request, pk):

    producto = get_object_or_404(
        Producto,
        codigo_producto=pk
    )

    if request.method == 'POST':

        form = ProductoForm(
            request.POST,
            request.FILES,
            instance=producto
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "✅ Producto actualizado correctamente"
            )

            return redirect('lista_productos_admin')

        else:

            messages.error(
                request,
                "❌ Error al actualizar"
            )

    else:

        form = ProductoForm(instance=producto)

    return render(request, 'productos/editar_producto.html', {
        'form': form,
    })


def eliminar_producto(request, pk):

    producto = get_object_or_404(
        Producto,
        codigo_producto=pk
    )

    producto.delete()

    messages.success(
        request,
        "✅ Producto eliminado correctamente"
    )

    return redirect('lista_productos_admin')


# =========================
# 🔥 STOCK
# =========================

def lista_stock(request):

    stocks = Stock.objects.select_related('producto')

    return render(request, 'productos/stock_admin.html', {
        'stocks': stocks,
        'titulo': "Stock de Productos"
    })


def editar_stock(request, pk):

    stock = get_object_or_404(
        Stock,
        pk=pk
    )

    if request.method == 'POST':

        form = StockForm(
            request.POST,
            instance=stock
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "✅ Stock actualizado correctamente"
            )

            return redirect('lista_stock')

        else:

            messages.error(
                request,
                "❌ Error al actualizar stock"
            )

    else:

        form = StockForm(instance=stock)

    return render(request, 'productos/editar_stock.html', {
        'form': form,
        'stock': stock,
        'titulo': f"Editar Stock - {stock.producto.nombre}"
    })


# =========================
# 🟡 COMPRAS ADMIN
# =========================

def registrar_compra(request):

    if request.method == 'POST':

        form_compra = CompraForm(request.POST)
        form_detalle = DetalleCompraForm(request.POST)

        if form_compra.is_valid() and form_detalle.is_valid():

            nueva_compra = form_compra.save()

            detalle = form_detalle.save(commit=False)

            detalle.compra = nueva_compra

            detalle.subtotal = (
                detalle.cantidad *
                detalle.producto.precio_venta
            )

            detalle.save()

            nueva_compra.total = detalle.subtotal
            nueva_compra.save()

            messages.success(
                request,
                "✅ Compra registrada exitosamente"
            )

            return redirect('historial_compras')

        else:

            messages.error(
                request,
                "❌ Corrige los errores del formulario"
            )

    else:

        form_compra = CompraForm()
        form_detalle = DetalleCompraForm()

    return render(request, 'productos/registrar_compra.html', {
        'form_compra': form_compra,
        'form_detalle': form_detalle,
        'titulo': "Registrar Nueva Compra"
    })


def historial_compras(request):

    compras = Compra.objects.all().order_by('-fecha_compra')

    return render(request, 'productos/historial_compras.html', {
        'compras': compras,
        'titulo': "Historial de Compras"
    })


def detalle_compra(request, pk):

    compra = get_object_or_404(
        Compra,
        codigo_compra=pk
    )

    detalles = compra.detalles.all()

    total = sum(d.subtotal for d in detalles)

    return render(request, 'productos/detalle_compra.html', {
        'compra': compra,
        'detalles': detalles,
        'total_calculado': total,
        'titulo': "Detalle de Compra"
    })


def eliminar_compra(request, pk):

    compra = get_object_or_404(
        Compra,
        codigo_compra=pk
    )

    if request.method == 'POST':

        compra.delete()

        messages.success(
            request,
            "✅ Compra eliminada"
        )

    return redirect('historial_compras')


# =========================
# 🛒 AGREGAR AL CARRITO
# =========================

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
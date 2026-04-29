from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Compra, Producto, DetalleCompra, Stock
from .forms import CompraForm, DetalleCompraForm, ProductoForm, StockForm
from django.http import JsonResponse
import json
from django.db import transaction


# =========================
# 🟢 CLIENTE
# =========================

def productos_galeria(request):
    productos = Producto.objects.all()
    return render(request, 'productos/productos_galeria.html', {
        'productos': productos
    })


# 🔥 YA NO USA SESSION (porque usas localStorage)
def carrito(request):
    return render(request, 'productos/carrito.html')


def pago(request):
    return render(request, 'productos/pago.html')


# 🔥 COMPRA REAL COMPLETA
def procesar_pago_cliente(request):
    if request.method == 'POST':

        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        metodo_pago = request.POST.get('pago')
        carrito_json = request.POST.get('carrito')

        # 🔴 Validar carrito
        if not carrito_json:
            messages.error(request, "❌ El carrito está vacío")
            return redirect('carrito')

        try:
            carrito = json.loads(carrito_json)
        except:
            messages.error(request, "❌ Error en el carrito")
            return redirect('carrito')

        if not carrito:
            messages.error(request, "❌ El carrito está vacío")
            return redirect('carrito')

        try:
            # 🔥 TRANSACCIÓN SEGURA
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

                # ✅ Crear detalles (el modelo hace TODO)
                for item in carrito:
                    producto = get_object_or_404(
                        Producto, 
                        codigo_producto=item['id']
                    )

                    DetalleCompra.objects.create(
                        compra=compra,
                        producto=producto,
                        cantidad=item['cantidad']
                    )

        except Exception as e:
            messages.error(request, f"❌ Error en la compra: {str(e)}")
            return redirect('carrito')

        # ✅ ÉXITO
        messages.success(request, "✅ Compra realizada con éxito")

        # 🔥 IMPORTANTE: esto limpia el carrito en el frontend
        return redirect('/productos/?compra=ok')

    return redirect('carrito')
# =========================
# 🔵 ADMIN PRODUCTOS
# =========================

def lista_productos_admin(request):
    productos = Producto.objects.all()
    return render(request, 'productos/productos_admin.html', {
        'productos': productos
    })


def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()

            # 🔥 CREA STOCK AUTOMÁTICO
            Stock.objects.get_or_create(producto=producto)

            messages.success(request, "✅ Producto creado correctamente")
            return redirect('lista_productos_admin')
        else:
            messages.error(request, "❌ Error al crear producto")
    else:
        form = ProductoForm()

    return render(request, 'productos/editar_producto.html', {
        'form': form
    })


def editar_producto(request, pk):
    producto = get_object_or_404(Producto, codigo_producto=pk)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto actualizado correctamente")
            return redirect('lista_productos_admin')
        else:
            messages.error(request, "❌ Error al actualizar")
    else:
        form = ProductoForm(instance=producto)

    return render(request, 'productos/editar_producto.html', {
        'form': form
    })


def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, codigo_producto=pk)
    producto.delete()
    messages.success(request, "✅ Producto eliminado correctamente")
    return redirect('lista_productos_admin')


# =========================
# 🔥 STOCK
# =========================

def lista_stock(request):
    stocks = Stock.objects.select_related('producto')
    return render(request, 'productos/stock_admin.html', {
        'stocks': stocks
    })


def editar_stock(request, pk):
    stock = get_object_or_404(Stock, pk=pk)

    if request.method == 'POST':
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Stock actualizado correctamente")
            return redirect('lista_stock')
        else:
            messages.error(request, "❌ Error al actualizar stock")
    else:
        form = StockForm(instance=stock)

    return render(request, 'productos/editar_stock.html', {
        'form': form,
        'stock': stock
    })


# =========================
# 🟡 COMPRAS (ADMIN)
# =========================

def historial_compras(request):
    compras = Compra.objects.all().order_by('-fecha_compra')
    return render(request, 'productos/historial_compras.html', {
        'compras': compras
    })


def detalle_compra(request, pk):
    compra = get_object_or_404(Compra, codigo_compra=pk)
    detalles = compra.detalles.all()

    total = sum(d.subtotal for d in detalles)

    return render(request, 'productos/detalle_compra.html', {
        'compra': compra,
        'detalles': detalles,
        'total_calculado': total
    })


def eliminar_compra(request, pk):
    compra = get_object_or_404(Compra, codigo_compra=pk)

    if request.method == 'POST':
        compra.delete()
        messages.success(request, "✅ Compra eliminada")

    return redirect('historial_compras')
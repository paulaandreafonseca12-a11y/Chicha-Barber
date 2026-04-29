from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Compra, Producto, DetalleCompra, Stock
from .forms import CompraForm, DetalleCompraForm, ProductoForm, StockForm
from django.http import JsonResponse
import json


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

        if not carrito_json:
            messages.error(request, "❌ El carrito está vacío")
            return redirect('carrito')

        carrito = json.loads(carrito_json)

        total = 0

        # ✅ CREAR COMPRA
        compra = Compra.objects.create(
            nombre_cliente=nombre,
            correo=correo,
            telefono=telefono,
            direccion=direccion,
            metodo_pago=metodo_pago,
            total=0
        )

        # 🔥 GUARDAR DETALLE
        for item in carrito:
            producto = Producto.objects.get(codigo_producto=item['id'])

            stock = Stock.objects.get(producto=producto)

            # 🚨 VALIDAR STOCK
            if stock.cantidad < item['cantidad']:
                messages.error(request, f"❌ Sin stock: {producto.nombre}")
                return redirect('carrito')

            subtotal = item['cantidad'] * float(item['precio'])
            total += subtotal

            DetalleCompra.objects.create(
                compra=compra,
                producto=producto,
                cantidad=item['cantidad'],
                precio=item['precio'],
                subtotal=subtotal
            )

            # 🔥 DESCONTAR STOCK
            stock.cantidad -= item['cantidad']
            stock.save()

        compra.total = total
        compra.save()

        messages.success(request, "✅ Compra realizada con éxito")

        return redirect('productos_galeria')

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
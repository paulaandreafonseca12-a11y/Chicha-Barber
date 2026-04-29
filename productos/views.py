from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Compra, Producto, DetalleCompra, Stock
from .forms import CompraForm, DetalleCompraForm, ProductoForm, StockForm
from django.http import JsonResponse

# =========================
# 🟢 VISTAS CLIENTE
# =========================

def productos_galeria(request):
    productos = Producto.objects.all()
    return render(request, 'productos/productos_galeria.html', {'productos': productos})


def carrito(request):
    carrito_items = request.session.get('carrito', {})
    return render(request, 'productos/carrito.html', {'carrito': carrito_items})


def pago(request):
    return render(request, 'productos/pago.html')


def procesar_pago_cliente(request):
    if request.method == 'POST':
        Compra.objects.create(
            nombre_cliente=request.POST.get('nombre'),
            correo=request.POST.get('correo'),
            telefono=request.POST.get('telefono'),
            direccion=request.POST.get('direccion'),
            metodo_pago=request.POST.get('metodo_pago'),
            total=request.POST.get('total')
        )
        messages.success(request, "✅ Pago realizado con éxito")
        return redirect('productos_galeria')

    return redirect('productos_galeria')


# =========================
# 🔵 ADMIN PRODUCTOS
# =========================

def lista_productos_admin(request):
    productos = Producto.objects.all()

    return render(request, 'productos/productos_admin.html', {
        'productos': productos
    })


# 🔥 CREAR PRODUCTO (SEPARADO)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()

            # 🔥 OPCIONAL: crear stock automático
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
# 🔥 STOCK (SEPARADO)
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
# 🟡 COMPRAS
# =========================

def registrar_compra(request):
    if request.method == 'POST':
        form_compra = CompraForm(request.POST)
        form_detalle = DetalleCompraForm(request.POST)

        if form_compra.is_valid() and form_detalle.is_valid():
            nueva_compra = form_compra.save()

            detalle = form_detalle.save(commit=False)
            detalle.compra = nueva_compra
            detalle.subtotal = detalle.cantidad * detalle.producto.precio_venta
            detalle.save()

            nueva_compra.total = detalle.subtotal
            nueva_compra.save()

            messages.success(request, "✅ Compra registrada exitosamente")
            return redirect('historial_compras')
        else:
            # Si hay errores en el POST, volvemos a renderizar la página con los errores
            messages.error(request, "❌ Por favor corrige los errores en el formulario.")
    else:
        # --- ESTO ES LO QUE TE FALTABA ---
        # Creamos los formularios vacíos para que el HTML los pueda dibujar
        form_compra = CompraForm()
        form_detalle = DetalleCompraForm()

    # El render DEBE ir fuera del if/else o en el bloque else para manejar el GET
    return render(request, 'productos/registrar_compra.html', {
        'form_compra': form_compra,
        'form_detalle': form_detalle
    })

def historial_compras(request):
    compras = Compra.objects.all().order_by('-fecha_compra')

    return render(request, 'productos/historial_compras.html', {
        'compras': compras,
        'form_compra': CompraForm(),
        'form_detalle': DetalleCompraForm()
    })


def detalle_compra(request, pk):
    compra = get_object_or_404(Compra, codigo_compra=pk)
    detalles = compra.detalles.all()

    total = sum(d.subtotal for d in detalles)
    compra.total = total
    compra.save(update_fields=['total'])

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
# =========================
# 🛒 CARRITO
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

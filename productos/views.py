from django.shortcuts import render, redirect, get_object_or_404
from .models import Compra, Producto
from django.contrib import messages
from .forms import CompraForm, DetalleCompraForm, ProductoForm

# --- VISTAS DE CLIENTES ---

def productos_galeria(request):
    productos = Producto.objects.all()
    return render(request, 'productos/productos_galeria.html', {
        'productos': productos
    })

from .models import Compra, Producto, DetalleCompra, Pago
from .forms import ProductoForm


# 🔹 LISTAR PRODUCTOS
def productos(request):
    productos = Producto.objects.all()
    return render(request, 'Productos.html', {'productos': productos})


# 🔹 CARRITO
def carrito(request):
    carrito_items = request.session.get('carrito', {})
    return render(request, 'productos/carrito.html', {
        'carrito': carrito_items
    })


# 🔹 PAGO
def pago(request):
    return render(request, 'productos/pago.html')

# --- VISTAS DEL ADMINISTRADOR ---

def lista_productos_admin(request):
    productos_listado = Producto.objects.all()
    form_compra = CompraForm()
    form_detalle = DetalleCompraForm()
    return render(request, 'productos/productos_admin.html', {
        'productos': productos_listado,
        'form_compra': form_compra,
        'form_detalle': form_detalle
    })

def registrar_compra(request):
    if request.method == 'POST':
        form_compra = CompraForm(request.POST)
        form_detalle = DetalleCompraForm(request.POST)
        if form_compra.is_valid() and form_detalle.is_valid():
            nueva_compra = form_compra.save()
            detalle = form_detalle.save(commit=False)
            detalle.compra = nueva_compra
            detalle.save()
            messages.success(request, "✅ Compra registrada exitosamente.")
            return redirect('historial_compras')  # ← redirige al historial
        else:
            # Muestra los errores
            messages.error(request, f"❌ Errores compra: {form_compra.errors}")
            messages.error(request, f"❌ Errores detalle: {form_detalle.errors}")
    return redirect('lista_productos_admin')

def historial_compras(request):
    compras_registradas = Compra.objects.all().order_by('-fecha_compra')
    return render(request, 'productos/historial_compras.html', {
        'compras': compras_registradas
    })

def detalle_compra(request, pk):
    compra = get_object_or_404(Compra, codigo_compra=pk)
    detalles = compra.detalles.all()
    return render(request, 'productos/detalle_compra.html', {
        'compra': compra,
        'detalles': detalles
    })

def editar_producto(request, pk):
    producto = get_object_or_404(Producto, codigo_producto=pk)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto actualizado correctamente.")
            return redirect('lista_productos_admin')
        else:
            messages.error(request, "❌ Error al actualizar. Revisa los campos.")
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'productos/editar_producto.html', {
        'form': form,
        'producto': producto
    })

def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, codigo_producto=pk)
    if request.method == 'POST':
        producto.delete()
        messages.success(request, "✅ Producto eliminado correctamente.")
        return redirect('lista_productos_admin')
    return render(request, 'productos/confirmar_eliminar.html', {
        'producto': producto
    })

def procesar_pago_cliente(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        correo = request.POST.get('correo')
        telefono = request.POST.get('telefono')
        direccion = request.POST.get('direccion')
        metodo_pago = request.POST.get('metodo_pago')
        total = request.POST.get('total')
        Compra.objects.create(
            nombre_cliente=nombre,
            correo=correo,
            telefono=telefono,
            direccion=direccion,
            metodo_pago=metodo_pago,
            total=total
        )
        messages.success(request, "✅ Pago realizado con éxito")
        return redirect('productos_galeria')
    return redirect('productos_galeria')

def crear_nuevo_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto creado exitosamente")
            return redirect('lista_productos_admin')
    else:
        form = ProductoForm()
    return render(request, 'productos/crear_producto.html', {'form': form})

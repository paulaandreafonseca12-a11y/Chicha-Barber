from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Compra, Producto, DetalleCompra
from .forms import CompraForm, DetalleCompraForm, ProductoForm

# --- VISTAS DE CLIENTES ---

def productos_galeria(request):
    productos = Producto.objects.all()
    return render(request, 'productos/productos_galeria.html', {'productos': productos})

# 🔹 LISTAR PRODUCTOS
def productos(request):
    productos = Producto.objects.all()
    return render(request, 'Productos.html', {'productos': productos})

def carrito(request):
    carrito_items = request.session.get('carrito', {})
    return render(request, 'productos/carrito.html', {'carrito': carrito_items})

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
            # Calcular subtotal
            detalle.subtotal = detalle.cantidad * detalle.producto.precio_venta
            detalle.save()
            # Actualizar total de la compra
            nueva_compra.total = detalle.subtotal
            nueva_compra.save()
            messages.success(request, "✅ Compra registrada exitosamente.")
            return redirect('historial_compras')
        else:
            messages.error(request, f"❌ Errores compra: {form_compra.errors}")
            messages.error(request, f"❌ Errores detalle: {form_detalle.errors}")
    return redirect('historial_compras')

def historial_compras(request):
    compras_registradas = Compra.objects.all().order_by('-fecha_compra')
    return render(request, 'productos/historial_compras.html', {
        'compras': compras_registradas,
        'form_compra': CompraForm(),       # ← agregar
        'form_detalle': DetalleCompraForm() # ← agregar
    })

def detalle_compra(request, pk):
    compra = get_object_or_404(Compra, codigo_compra=pk)
    detalles = compra.detalles.all()
    
    # Recalcular y guardar el total siempre
    total_real = sum(d.subtotal for d in detalles)
    compra.total = total_real
    compra.save(update_fields=['total'])
    
    return render(request, 'productos/detalle_compra.html', {
        'compra': compra,
        'detalles': detalles,
        'total_calculado': total_real  # también lo pasamos directo
    })

def eliminar_compra(request, pk):
    compra = get_object_or_404(Compra, codigo_compra=pk)
    if request.method == 'POST':
        compra.delete()
        messages.success(request, "✅ Compra eliminada correctamente.")
    return redirect('historial_compras')

def editar_producto(request, pk):
    producto = get_object_or_404(Producto, codigo_producto=pk)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)  # 🔥 AQUÍ
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
    producto.delete()
    messages.success(request, "✅ Producto eliminado correctamente.")
    return redirect('lista_productos_admin')

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

def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
       
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto creado exitosamente")
            return redirect('lista_productos_admin')
    else:
        form = ProductoForm()
    return render(request, 'productos/crear_producto.html', {'form': form})
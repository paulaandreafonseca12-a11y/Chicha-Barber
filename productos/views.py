from django.shortcuts import render, redirect
from .models import Compra, Producto
from django.contrib import messages
from .forms import CompraForm, DetalleCompraForm, ProductoForm

# --- VISTAS DE CLIENTES ---

def productos_galeria(request):
    productos = Producto.objects.all()
    return render(request, 'productos/productos_galeria.html', {
        'productos': productos
    })

def carrito(request):
    carrito_items = request.session.get('carrito', {})
    return render(request, 'productos/carrito.html', {
        'carrito': carrito_items
    })

def pago(request):
    return render(request, 'productos/pago.html')

# --- VISTAS DEL ADMINISTRADOR (sin cambios) ---

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
            messages.success(request, "✅ Compra registrada y total calculado exitosamente.")
            return redirect('productos:lista_productos_admin')
    return redirect('productos:lista_productos_admin')

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
        return redirect('productos:productos_galeria')
    return redirect('productos:productos_galeria')

def crear_nuevo_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Producto creado exitosamente")
            return redirect('productos:lista_productos_admin')
    else:
        form = ProductoForm()
    return render(request, 'crear_producto.html', {'form': form})

def historial_compras(request):
    compras_registradas = Compra.objects.all().order_by('-fecha_compra')
    return render(request, 'productos/historial_compras.html', {
        'compras': compras_registradas
    })
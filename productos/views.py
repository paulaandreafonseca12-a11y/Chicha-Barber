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
            return redirect('productos:historial_compras')  # ← redirige al historial
        else:
            # Muestra los errores
            messages.error(request, f"❌ Errores compra: {form_compra.errors}")
            messages.error(request, f"❌ Errores detalle: {form_detalle.errors}")
    return redirect('productos:lista_productos_admin')

        try:
            # 📥 Datos del cliente
            nombre = request.POST.get('nombre')
            correo = request.POST.get('correo')
            telefono = request.POST.get('telefono')
            direccion = request.POST.get('direccion')
            metodo_pago = request.POST.get('pago')

            # 📦 Carrito (JSON)
            carrito_data = request.POST.get('carrito')

            if not carrito_data:
                messages.error(request, "❌ Carrito vacío")
                return redirect('productos')

            carrito = json.loads(carrito_data)

            total = 0

            # 🧾 Crear compra
            compra = Compra.objects.create(
                nombre_cliente=nombre,
                correo=correo,
                telefono=telefono,
                direccion=direccion,
                metodo_pago=metodo_pago,
                total=0
            )

            # 🔁 Recorrer carrito
            for item in carrito:

                try:
                    producto = Producto.objects.get(nombre=item["nombre"])
                except Producto.DoesNotExist:
                    messages.error(request, f"❌ Producto no encontrado: {item['nombre']}")
                    continue

                cantidad = int(item["cantidad"])

                # ⚠️ Validar stock
                if producto.stock.cantidad < cantidad:
                    messages.error(request, f"❌ Stock insuficiente para {producto.nombre}")
                    continue

                subtotal = producto.precio_venta * cantidad
                total += subtotal

                # 🧾 Guardar detalle
                DetalleCompra.objects.create(
                    producto=producto,
                    compra=compra,
                    cantidad=cantidad,
                    subtotal=subtotal
                )

                # 📉 Actualizar stock
                producto.stock.cantidad -= cantidad
                producto.stock.save()

            # 💰 Actualizar total
            compra.total = total
            compra.save()

            # 💳 Guardar pago
            Pago.objects.create(
                compra=compra,
                nombre=nombre,
                correo=correo,
                telefono=telefono,
                direccion=direccion,
                metodo_pago=metodo_pago
            )

            messages.success(request, "✅ Compra realizada con éxito")

            return redirect('productos')

        except Exception as e:
            print("ERROR:", e)
            messages.error(request, "❌ Ocurrió un error al procesar la compra")
            return redirect('productos')

    return redirect('productos')


# 🔹 CREAR PRODUCTO (ADMIN)
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Producto creado correctamente")
            return redirect('crear_producto')
    else:
        form = ProductoForm()

    return render(request, 'crear_producto.html', {'form': form})

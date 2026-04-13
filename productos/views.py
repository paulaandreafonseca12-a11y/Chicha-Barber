import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .models import Compra, Producto, DetalleCompra, Pago
from .forms import ProductoForm


# 🔹 LISTAR PRODUCTOS
def productos(request):
    productos = Producto.objects.all()
    return render(request, 'Productos.html', {'productos': productos})


# 🔹 CARRITO
def carrito(request):
    return render(request, 'Carrito.html')


# 🔹 PAGO
def pago(request):
    return render(request, 'pago.html')

def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'admin/productos/lista.html', {'productos': productos})

# 🔥 PROCESAR COMPRA (VERSIÓN PRO)
def procesar_compra(request):
    if request.method == 'POST':

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
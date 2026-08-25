from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Producto, Categoria, Proveedor, Marca, DetalleProducto
from .forms import ProductoForm, CategoriaForm, ProveedorForm, MarcaForm, DetalleProductoForm


# ==========================================================
# 🟢 CLIENTE - GALERÍA DE PRODUCTOS
# ==========================================================

def productos_galeria(request):
    buscar = request.GET.get('buscar', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()
    marca_id = request.GET.get('marca', '').strip()

    productos = Producto.objects.filter(
        estado=True
    ).select_related(
        'codigo_categoria',
        'codigo_marca',
        'codigo_detalle_producto'
    )

    if buscar:
        productos = productos.filter(
            Q(nombre__icontains=buscar) |
            Q(descripcion__icontains=buscar) |
            Q(codigo_categoria__nombre__icontains=buscar) |
            Q(codigo_marca__nombre__icontains=buscar)
        )

    if categoria_id and categoria_id.isdigit():
        productos = productos.filter(
            codigo_categoria_id=int(categoria_id)
        )

    if marca_id and marca_id.isdigit():
        productos = productos.filter(
            codigo_marca_id=int(marca_id)
        )

    context = {
        'titulo': 'Galería de Productos',
        'productos': productos,
        'categorias': Categoria.objects.all().order_by('nombre'),
        'marcas': Marca.objects.filter(estado=True).order_by('nombre'),
        'categoria_seleccionada': int(categoria_id) if categoria_id and categoria_id.isdigit() else None,
        'marca_seleccionada': int(marca_id) if marca_id and marca_id.isdigit() else None,
        'buscar': buscar,
    }

    return render(
        request,
        'catalogo/productos/Productos_galeria.html',
        context
    )


# ==========================================================
# 🔵 ADMIN - GESTIÓN DE PRODUCTOS
# ==========================================================

@login_required
def lista_productos_admin(request):
    productos = Producto.objects.select_related(
        'codigo_categoria',
        'codigo_marca',
        'codigo_detalle_producto'
    ).all().order_by('-codigo_producto')

    total_productos = Producto.objects.count()
    activos = Producto.objects.filter(estado=True).count()
    inactivos = Producto.objects.filter(estado=False).count()

    context = {
        'titulo': 'Lista de Productos',
        'productos': productos,
        'total_productos': total_productos,
        'activos': activos,
        'inactivos': inactivos,
    }

    return render(
        request,
        'catalogo/productos/productos_admin.html',
        context
    )


@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES)
        if form.is_valid():
            producto = form.save()
            messages.success(request, f"Producto '{producto.nombre}' creado correctamente.")
            return redirect('lista_productos_admin')
    else:
        form = ProductoForm()

    return render(
        request,
        'catalogo/productos/crear_producto.html',
        {
            'titulo': 'Crear Producto',
            'form': form
        }
    )


@login_required
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, codigo_producto=pk)

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, f"Producto '{producto.nombre}' actualizado correctamente.")
            return redirect('lista_productos_admin')
    else:
        form = ProductoForm(instance=producto)

    return render(
        request,
        'catalogo/productos/editar_producto.html',
        {
            'titulo': 'Editar Producto',
            'form': form,
            'producto': producto
        }
    )


@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, codigo_producto=pk)
    nombre = producto.nombre
    producto.delete()
    messages.success(request, f"Producto '{nombre}' eliminado correctamente.")
    return redirect('lista_productos_admin')


# ==========================================================
# 🟣 CATEGORÍAS
# ==========================================================

@login_required
def lista_categorias(request):
    categorias = Categoria.objects.all().order_by('nombre')
    return render(
        request,
        'catalogo/categorias/lista_categoria.html',
        {
            'titulo': 'Categorías',
            'categorias': categorias
        }
    )


@login_required
def crear_categoria(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save()
            messages.success(request, f"Categoría '{categoria.nombre}' creada correctamente.")
            return redirect('lista_categorias')
    else:
        form = CategoriaForm()

    return render(
        request,
        'catalogo/categorias/crear_categoria.html',
        {
            'titulo': 'Crear Categoría',
            'form': form
        }
    )


@login_required
def editar_categoria(request, id):
    categoria = get_object_or_404(Categoria, codigo=id)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, f"Categoría '{categoria.nombre}' actualizada correctamente.")
            return redirect('lista_categorias')
    else:
        form = CategoriaForm(instance=categoria)

    return render(
        request,
        'catalogo/categorias/editar_categoria.html',
        {
            'titulo': 'Editar Categoría',
            'form': form,
            'categoria': categoria
        }
    )


@login_required
def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, codigo=id)
    nombre = categoria.nombre
    categoria.delete()
    messages.success(request, f"Categoría '{nombre}' eliminada correctamente.")
    return redirect('lista_categorias')


# ==========================================================
# 🟣 PROVEEDORES
# ==========================================================

@login_required
def lista_proveedores(request):
    proveedores = Proveedor.objects.all().order_by('nombre')
    return render(
        request,
        'catalogo/proveedores/lista_proveedores.html',
        {
            'titulo': 'Proveedores',
            'proveedores': proveedores
        }
    )


@login_required
def crear_proveedor(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            messages.success(request, f"Proveedor '{proveedor.nombre}' creado correctamente.")
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm()

    return render(
        request,
        'catalogo/proveedores/crear_proveedor.html',
        {
            'titulo': 'Crear Proveedor',
            'form': form
        }
    )


@login_required
def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, codigo=id)

    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, f"Proveedor '{proveedor.nombre}' actualizado correctamente.")
            return redirect('lista_proveedores')
    else:
        form = ProveedorForm(instance=proveedor)

    return render(
        request,
        'catalogo/proveedores/editar_proveedor.html',
        {
            'titulo': 'Editar Proveedor',
            'form': form,
            'proveedor': proveedor
        }
    )


@login_required
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, codigo=id)
    nombre = proveedor.nombre
    proveedor.delete()
    messages.success(request, f"Proveedor '{nombre}' eliminado correctamente.")
    return redirect('lista_proveedores')


# ==========================================================
# 🏷️ MARCAS
# ==========================================================

@login_required
def lista_marcas(request):
    marcas = Marca.objects.all().prefetch_related('productos').order_by('nombre')
    total_marcas = Marca.objects.count()
    marcas_activas = Marca.objects.filter(estado=True).count()
    marcas_inactivas = Marca.objects.filter(estado=False).count()

    return render(
        request,
        'catalogo/marca/marca.html',
        {
            'titulo': 'Marcas',
            'marcas': marcas,
            'total_marcas': total_marcas,
            'marcas_activas': marcas_activas,
            'marcas_inactivas': marcas_inactivas,
        }
    )


@login_required
def crear_marca(request):
    if request.method == 'POST':
        form = MarcaForm(request.POST)
        if form.is_valid():
            marca = form.save()
            messages.success(request, f"Marca '{marca.nombre}' creada correctamente.")
            return redirect('lista_marcas')
    else:
        form = MarcaForm()

    return render(
        request,
        'catalogo/marca/crear_marca.html',
        {
            'titulo': 'Crear Marca',
            'form': form,
        }
    )


@login_required
def editar_marca(request, id):
    marca = get_object_or_404(Marca, codigo=id)

    if request.method == 'POST':
        form = MarcaForm(request.POST, instance=marca)
        if form.is_valid():
            form.save()
            messages.success(request, f"Marca '{marca.nombre}' actualizada correctamente.")
            return redirect('lista_marcas')
    else:
        form = MarcaForm(instance=marca)

    return render(
        request,
        'catalogo/marca/editar_marca.html',
        {
            'titulo': 'Editar Marca',
            'form': form,
            'marca': marca,
        }
    )


@login_required
def eliminar_marca(request, id):
    marca = get_object_or_404(Marca, codigo=id)

    if request.method == 'POST':
        nombre = marca.nombre
        marca.delete()
        messages.success(request, f"Marca '{nombre}' eliminada correctamente.")
        return redirect('lista_marcas')

    return render(
        request,
        'catalogo/marca/eliminar_marca.html',
        {
            'titulo': 'Eliminar Marca',
            'marca': marca,
        }
    )

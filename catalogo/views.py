
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.db.models.deletion import ProtectedError
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from usuarios.models import RolUsuario

from .models import (
    Producto,
    Categoria,
    Proveedor,
    Marca,
    DetalleProducto,
    MovimientoProducto,
    Promocion,
)

from .forms import (
    ProductoForm,
    CategoriaForm,
    ProveedorForm,
    MarcaForm,
    DetalleProductoForm,
    EditarExistenciasForm,
    PromocionForm,
    PromocionEditarForm,
)


# ==========================================================
# CLIENTE - GALERÍA DE PRODUCTOS
# ==========================================================

def productos_galeria(request):
    buscar = request.GET.get('buscar', '').strip()
    categoria_id = request.GET.get('categoria', '').strip()
    marca_id = request.GET.get('marca', '').strip()

    productos = (
        Producto.objects
        .filter(estado=True)
        .select_related(
            'codigo_categoria',
            'codigo_marca',
            'codigo_detalle_producto'
        )
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
        'marcas': Marca.objects.filter(
            estado=True
        ).order_by('nombre'),
        'categoria_seleccionada': (
            int(categoria_id)
            if categoria_id and categoria_id.isdigit()
            else None
        ),
        'marca_seleccionada': (
            int(marca_id)
            if marca_id and marca_id.isdigit()
            else None
        ),
        'buscar': buscar,
    }

    return render(
        request,
        'catalogo/productos/Productos_galeria.html',
        context
    )


# ==========================================================
# ADMIN - GESTIÓN DE PRODUCTOS
# ==========================================================

@login_required
def lista_productos_admin(request):
    productos = (
        Producto.objects
        .select_related(
            'codigo_categoria',
            'codigo_marca',
            'codigo_detalle_producto'
        )
        .all()
        .order_by('-codigo_producto')
    )

    context = {
        'titulo': 'Lista de Productos',
        'productos': productos,
        'total_productos': Producto.objects.count(),
        'activos': Producto.objects.filter(estado=True).count(),
        'inactivos': Producto.objects.filter(estado=False).count(),
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

            messages.success(
                request,
                f"Producto '{producto.nombre}' creado correctamente."
            )

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
            producto = form.save()

            messages.success(
                request,
                f"Producto '{producto.nombre}' actualizado correctamente."
            )

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
@require_POST
def eliminar_producto(request, pk):
    producto = get_object_or_404(
        Producto,
        codigo_producto=pk
    )

    nombre = producto.nombre

    try:
        producto.delete()

        messages.success(
            request,
            f"Producto '{nombre}' eliminado correctamente."
        )

    except ProtectedError:
        messages.error(
            request,
            (
                f"No se puede eliminar '{nombre}' porque tiene "
                "registros asociados a compras o ventas. "
                "El producto se conserva para proteger el historial. "
                "Puedes desactivarlo si ya no deseas utilizarlo."
            )
        )

    return redirect('lista_productos_admin')


# ==========================================================
# CATEGORÍAS
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
    is_json = (
        'application/json' in request.META.get('CONTENT_TYPE', '') or
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        (request.body and request.body.startswith(b'{'))
    )

    if is_json:
        if request.method != 'POST':
            return JsonResponse(
                {'success': False, 'error': 'Método no permitido.'},
                status=405
            )

        try:
            data = json.loads(request.body)
            nombre = data.get('nombre', '').strip()
            descripcion = data.get('descripcion', '').strip()

            if not nombre:
                return JsonResponse(
                    {
                        'success': False,
                        'error': 'El nombre de la categoría es obligatorio.'
                    },
                    status=400
                )

            if Categoria.objects.filter(nombre__iexact=nombre).exists():
                return JsonResponse(
                    {
                        'success': False,
                        'error': 'Ya existe una categoría con ese nombre.'
                    },
                    status=400
                )

            categoria = Categoria.objects.create(
                nombre=nombre,
                descripcion=descripcion
            )

            return JsonResponse({
                'success': True,
                'codigo': categoria.codigo,
                'nombre': categoria.nombre,
                'descripcion': categoria.descripcion or '',
                'mensaje': f"Categoría '{categoria.nombre}' creada correctamente."
            })

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Los datos enviados no tienen un formato válido.'
                },
                status=400
            )
        except Exception:
            return JsonResponse(
                {
                    'success': False,
                    'error': 'No se pudo crear la categoría.'
                },
                status=500
            )

    if request.method == 'POST':
        form = CategoriaForm(request.POST)

        if form.is_valid():
            categoria = form.save()

            messages.success(
                request,
                f"Categoría '{categoria.nombre}' creada correctamente."
            )

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
            categoria = form.save()

            messages.success(
                request,
                f"Categoría '{categoria.nombre}' actualizada correctamente."
            )

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
@require_POST
def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, codigo=id)
    nombre = categoria.nombre

    try:
        categoria.delete()
        messages.success(
            request,
            f"Categoría '{nombre}' eliminada correctamente."
        )
    except ProtectedError:
        messages.error(
            request,
            f"No se puede eliminar '{nombre}' porque tiene registros asociados."
        )

    return redirect('lista_categorias')


# ==========================================================
# PROVEEDORES
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

            messages.success(
                request,
                f"Proveedor '{proveedor.nombre}' creado correctamente."
            )

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
            proveedor = form.save()

            messages.success(
                request,
                f"Proveedor '{proveedor.nombre}' actualizado correctamente."
            )

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
@require_POST
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, codigo=id)
    nombre = proveedor.nombre

    try:
        proveedor.delete()
        messages.success(
            request,
            f"Proveedor '{nombre}' eliminado correctamente."
        )
    except ProtectedError:
        messages.error(
            request,
            f"No se puede eliminar '{nombre}' porque tiene registros asociados."
        )

    return redirect('lista_proveedores')


# ==========================================================
# MARCAS
# ==========================================================

@login_required
def lista_marcas(request):
    marcas = (
        Marca.objects
        .prefetch_related('productos')
        .order_by('nombre')
    )

    return render(
        request,
        'catalogo/marca/marca.html',
        {
            'titulo': 'Marcas',
            'marcas': marcas,
            'total_marcas': Marca.objects.count(),
            'marcas_activas': Marca.objects.filter(estado=True).count(),
            'marcas_inactivas': Marca.objects.filter(estado=False).count(),
        }
    )


@login_required
def crear_marca(request):
    is_json = (
        'application/json' in request.META.get('CONTENT_TYPE', '') or
        request.headers.get('x-requested-with') == 'XMLHttpRequest' or
        (request.body and request.body.startswith(b'{'))
    )

    if is_json:
        if request.method != 'POST':
            return JsonResponse(
                {'success': False, 'error': 'Método no permitido.'},
                status=405
            )

        try:
            data = json.loads(request.body)
            nombre = data.get('nombre', '').strip()
            descripcion = data.get('descripcion', '').strip()
            estado = data.get('estado', True)

            if isinstance(estado, str):
                estado = estado.lower() in [
                    'true', '1', 'si', 'sí', 'activo'
                ]

            if not nombre:
                return JsonResponse(
                    {
                        'success': False,
                        'error': 'El nombre de la marca es obligatorio.'
                    },
                    status=400
                )

            if Marca.objects.filter(nombre__iexact=nombre).exists():
                return JsonResponse(
                    {
                        'success': False,
                        'error': 'Ya existe una marca con ese nombre.'
                    },
                    status=400
                )

            marca = Marca.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                estado=estado
            )

            return JsonResponse({
                'success': True,
                'codigo': marca.codigo,
                'nombre': marca.nombre,
                'descripcion': marca.descripcion or '',
                'estado': marca.estado,
                'mensaje': f"Marca '{marca.nombre}' creada correctamente."
            })

        except json.JSONDecodeError:
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Los datos enviados no tienen un formato válido.'
                },
                status=400
            )
        except Exception:
            return JsonResponse(
                {
                    'success': False,
                    'error': 'No se pudo crear la marca.'
                },
                status=500
            )

    if request.method == 'POST':
        form = MarcaForm(request.POST)

        if form.is_valid():
            marca = form.save()

            messages.success(
                request,
                f"Marca '{marca.nombre}' creada correctamente."
            )

            return redirect('lista_marcas')
    else:
        form = MarcaForm()

    return render(
        request,
        'catalogo/marca/crear_marca.html',
        {
            'titulo': 'Crear Marca',
            'form': form
        }
    )


@login_required
def editar_marca(request, id):
    marca = get_object_or_404(Marca, codigo=id)

    if request.method == 'POST':
        form = MarcaForm(request.POST, instance=marca)

        if form.is_valid():
            marca = form.save()

            messages.success(
                request,
                f"Marca '{marca.nombre}' actualizada correctamente."
            )

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

        try:
            marca.delete()
            messages.success(
                request,
                f"Marca '{nombre}' eliminada correctamente."
            )
        except ProtectedError:
            messages.error(
                request,
                f"No se puede eliminar '{nombre}' porque tiene productos asociados."
            )

        return redirect('lista_marcas')

    return render(
        request,
        'catalogo/marca/eliminar_marca.html',
        {
            'titulo': 'Eliminar Marca',
            'marca': marca,
        }
    )


# ==========================================================
# EXISTENCIAS / DETALLE DE PRODUCTOS
# ==========================================================

@login_required
def lista_existencias(request):
    existenciass = (
        DetalleProducto.objects
        .prefetch_related(
            'producto_principal__codigo_categoria',
            'producto_principal__codigo_marca'
        )
        .all()
        .order_by('codigo')
    )

    context = {
        'titulo': 'Detalle de Productos',
        'existenciass': existenciass,
        'total_existencias': existenciass.count(),
        'stock_total': sum(
            existencia.cantidad_actual for existencia in existenciass
        ),
        'stock_bajo': existenciass.filter(
            cantidad_actual__lte=10
        ).count(),
    }

    return render(
        request,
        'catalogo/detalle_producto/detalle_producto.html',
        context
    )


@login_required
def editar_existencias(request, pk):
    detalle = get_object_or_404(DetalleProducto, pk=pk)
    producto = detalle.producto_principal.first()

    if request.method == 'POST':
        form = EditarExistenciasForm(
            request.POST,
            instance=detalle
        )

        if form.is_valid():
            form.save()

            nombre_producto = (
                producto.nombre if producto
                else f"Detalle #{detalle.codigo}"
            )

            messages.success(
                request,
                f"Cantidad de '{nombre_producto}' actualizada correctamente."
            )

            return redirect('lista_existencias')

        messages.error(
            request,
            "No se pudo guardar la cantidad. Revisa los errores del formulario."
        )
    else:
        form = EditarExistenciasForm(instance=detalle)

    ultima_adquisicion = None

    if producto:
        ultima_adquisicion = (
            producto.adquisiciones
            .order_by('-codigo')
            .first()
        )

    return render(
        request,
        'catalogo/detalle_producto/editar_detalle_producto.html',
        {
            'titulo': 'Editar Existencias',
            'form': form,
            'existencias': detalle,
            'ultima_adquisicion': ultima_adquisicion,
            'producto': producto,
        }
    )


# ==========================================================
# MOVIMIENTOS DE EXISTENCIAS
# ==========================================================

@login_required
def lista_movimientos_existencias(request):
    movimientos = (
        MovimientoProducto.objects
        .select_related('codigo_detalle_producto')
        .prefetch_related(
            'codigo_detalle_producto__producto_principal'
        )
        .order_by('-fecha')
    )

    return render(
        request,
        'catalogo/detalle_producto/movimiento_producto.html',
        {
            'titulo': 'Movimientos de productos',
            'movimientos': movimientos,
            'total_movimientos': movimientos.count(),
            'total_entradas': movimientos.filter(tipo='entrada').count(),
            'total_salidas': movimientos.filter(tipo='salida').count(),
        }
    )


@login_required
def registrar_movimiento_existencias(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        tipo = request.POST.get('tipo')
        cantidad_str = request.POST.get('cantidad', '1')
        motivo = request.POST.get('motivo', '').strip()

        try:
            cantidad = int(cantidad_str)
        except (ValueError, TypeError):
            messages.error(request, "La cantidad ingresada no es válida.")
            return redirect('registrar_movimiento_existencias')

        if cantidad <= 0:
            messages.error(request, "La cantidad debe ser mayor a cero.")
            return redirect('registrar_movimiento_existencias')

        if tipo not in ['entrada', 'salida']:
            messages.error(request, "Tipo de movimiento inválido.")
            return redirect('registrar_movimiento_existencias')

        producto = get_object_or_404(
            Producto,
            codigo_producto=producto_id
        )

        detalle = producto.codigo_detalle_producto

        if not detalle:
            messages.error(
                request,
                f"El producto '{producto.nombre}' no tiene detalle de inventario."
            )
            return redirect('registrar_movimiento_existencias')

        with transaction.atomic():
            detalle = DetalleProducto.objects.select_for_update().get(
                pk=detalle.pk
            )

            if tipo == 'salida' and detalle.cantidad_actual < cantidad:
                messages.error(
                    request,
                    f"Stock insuficiente. Stock actual: {detalle.cantidad_actual}"
                )
                return redirect('registrar_movimiento_existencias')

            if tipo == 'entrada':
                detalle.cantidad_actual += cantidad
            else:
                detalle.cantidad_actual -= cantidad

            detalle.save(
                update_fields=['cantidad_actual', 'fecha_actualizacion']
            )

            MovimientoProducto.objects.create(
                codigo_detalle_producto=detalle,
                tipo=tipo,
                cantidad=cantidad,
                observacion=(
                    motivo or (
                        'Entrada manual' if tipo == 'entrada'
                        else 'Salida manual'
                    )
                )
            )

        messages.success(
            request,
            f"Movimiento de {tipo} ({cantidad} unidades) registrado con éxito."
        )

        return redirect('lista_movimientos_existencias')

    productos = (
        Producto.objects
        .filter(estado=True)
        .select_related('codigo_detalle_producto')
        .order_by('nombre')
    )

    return render(
        request,
        'catalogo/detalle_producto/movimiento_producto_registar.html',
        {
            'titulo': 'Registrar Movimiento',
            'productos': productos,
        }
    )


@login_required
def eliminar_movimiento_existencias(request, pk):
    movimiento = get_object_or_404(MovimientoProducto, pk=pk)
    detalle = movimiento.codigo_detalle_producto

    if request.method == 'POST':
        if not detalle:
            messages.error(
                request,
                "El movimiento no tiene un detalle de producto asociado."
            )
            return redirect('lista_movimientos_existencias')

        with transaction.atomic():
            detalle = DetalleProducto.objects.select_for_update().get(
                pk=detalle.pk
            )

            if movimiento.tipo == 'entrada':
                if detalle.cantidad_actual < movimiento.cantidad:
                    messages.error(
                        request,
                        "No se puede revertir el movimiento porque el stock actual es insuficiente."
                    )
                    return redirect('lista_movimientos_existencias')

                detalle.cantidad_actual -= movimiento.cantidad

            elif movimiento.tipo == 'salida':
                detalle.cantidad_actual += movimiento.cantidad

            detalle.save(
                update_fields=['cantidad_actual', 'fecha_actualizacion']
            )

            movimiento.delete()

        messages.success(
            request,
            "Movimiento eliminado y stock ajustado correctamente."
        )

        return redirect('lista_movimientos_existencias')

    producto = (
        detalle.producto_principal.first()
        if detalle else None
    )

    return render(
        request,
        'catalogo/detalle_producto/movimiento_producto_eliminar.html',
        {
            'titulo': 'Eliminar Movimiento',
            'movimiento': movimiento,
            'producto': producto,
        }
    )


# ==========================================================
# PROMOCIONES
# ==========================================================

def promocion(request):
    promociones = Promocion.objects.all()

    return render(
        request,
        'catalogo/promocion/promocion.html',
        {
            'titulo': 'Promociones',
            'promociones': promociones
        }
    )


def listado_promocion(request):
    promociones = Promocion.objects.all()

    return render(
        request,
        'catalogo/promocion/listado-promocion.html',
        {
            'titulo': 'Listado de Promociones',
            'promociones': promociones,
            'total_promociones': promociones.count(),
            'activas': promociones.filter(estado=True).count(),
            'inactivas': promociones.filter(estado=False).count(),
        }
    )


@login_required
def crear_promocion(request):
    if not (
        request.user.is_staff or
        getattr(request.user, 'rol', None) == RolUsuario.ADMIN
    ):
        messages.error(request, "Acceso denegado.")
        return redirect('listado-promocion')

    if request.method == 'POST':
        form = PromocionForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            messages.success(request, "Promoción creada exitosamente.")
            return redirect('listado-promocion')

        messages.error(
            request,
            "Error al crear la promoción. Por favor revisa los campos."
        )
    else:
        form = PromocionForm()

    return render(
        request,
        'catalogo/promocion/agregar_promocion.html',
        {
            'form': form,
            'titulo': 'Crear Nueva Promoción'
        }
    )


@login_required
def editar_promocion(request, pk):
    if not (
        request.user.is_staff or
        getattr(request.user, 'rol', None) == RolUsuario.ADMIN
    ):
        messages.error(request, "Acceso denegado.")
        return redirect('listado-promocion')

    promocion_obj = get_object_or_404(Promocion, pk=pk)

    if request.method == 'POST':
        form = PromocionEditarForm(
            request.POST,
            request.FILES,
            instance=promocion_obj
        )

        if form.is_valid():
            promocion_obj = form.save()

            messages.success(
                request,
                f"Promoción {promocion_obj.nombre} actualizada."
            )

            return redirect('listado-promocion')
    else:
        form = PromocionEditarForm(instance=promocion_obj)

    return render(
        request,
        'catalogo/promocion/editar_promocion.html',
        {
            'form': form,
            'promocion': promocion_obj
        }
    )


@login_required
def eliminar_promocion(request, pk):
    if not (
        request.user.is_staff or
        getattr(request.user, 'rol', None) == RolUsuario.ADMIN
    ):
        messages.error(request, "Acceso denegado.")
        return redirect('listado-promocion')

    promocion_obj = get_object_or_404(Promocion, pk=pk)

    if request.method == 'POST':
        promocion_obj.delete()
        messages.success(request, "Promoción eliminada.")
        return redirect('listado-promocion')

    return render(
        request,
        'catalogo/promocion/eliminar_promocion.html',
        {
            'promocion': promocion_obj
        }
    )

from django.db.models import DecimalField, F, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone

from catalogo.models import Categoria, Marca, Producto, Promocion
from compra.models import DetalleCompra
from servicios.models import Servicios


CONTEXTO_ADMIN_BASE = """
Eres ChichaBot, el asistente de soporte técnico y gestión operativa del Panel de Administración de Chicha Barber Studio.

Tus funciones y reglas en este modo:
- Ayudas a los administradores y barberos a gestionar el sistema.
- Para productos, categorías y marcas, indica la ruta exacta: menú "Catálogo de Productos" → "Lista de Productos", "Categorías" o "Marcas", respectivamente.
- Para crear un producto, guía a "Catálogo de Productos" → "Lista de Productos" y luego al botón "Nuevo Producto".
- En el formulario de producto también se puede crear una categoría o marca con el botón "+" junto al campo correspondiente. La categoría es obligatoria; la marca es opcional.
- Para inventario, indica la ruta "Inventario de Productos" → "Detalle Producto" o "Movimiento de productos". No digas que las categorías están en Inventario.
- Para proveedores, adquisiciones y ventas, indica "Compras & Ventas" → "Proveedores", "Compras" o "Ventas", respectivamente.
- Para promociones, indica "Ofertas y Promos" → "Lista de promociones".
- Para servicios, indica "Gestión de Servicios" → "Lista de servicios"; para reservas, "Reservas" → "Ver Agenda".
- Indica cómo consultar facturas e historial de ventas desde "Compras & Ventas" → "Ventas", y la bitácora desde "Inventario de Productos" → "Bitácora".
- Respondes únicamente sobre tareas y funciones administrativas disponibles en el panel.
- No guías procesos de clientes, como registrarse, iniciar sesión, comprar, usar el carrito o reservar citas desde la página pública.
- No realizas cambios en el sistema; explicas cómo hacerlos desde las secciones del panel.
- Usa los nombres exactos de las secciones anteriores. No inventes rutas, opciones ni botones; si no conoces el nombre de una acción, indica la sección comprobada y pide que revisen las opciones visibles.
- Si la pregunta no es administrativa, explica brevemente que solo puedes ayudar con la gestión del panel.
- Respondes de forma breve, clara, cordial y en formato tipo chat (WhatsApp).
- Si te preguntan sobre un proceso administrativo, indícales la sección del panel donde deben ir.
"""


def obtener_contexto_admin():
    """Construye el contexto administrativo usando campos y relaciones reales."""
    ultima_adquisicion = (
        DetalleCompra.objects.filter(codigo_producto_id=OuterRef("pk"))
        .order_by("-codigo_compra__fecha", "-codigo")
        .values("precio_venta")[:1]
    )
    productos = (
        Producto.objects.annotate(
            precio_venta_contexto=Coalesce(
                Subquery(ultima_adquisicion),
                F("precio"),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )
        .select_related(
            "codigo_categoria",
            "codigo_marca",
            "codigo_detalle_producto",
        )
    )
    categorias = Categoria.objects.all()
    marcas = Marca.objects.all()
    servicios = Servicios.objects.all()
    promociones = Promocion.objects.select_related(
        "codigo_producto",
        "codigo_servicio",
    )

    contexto = (
        CONTEXTO_ADMIN_BASE
        + "\n\n=== DATOS DEL SISTEMA PARA ADMINISTRACIÓN ===\n"
    )

    contexto += "\n--- PRODUCTOS, PRECIO, MARCA, CATEGORÍA Y EXISTENCIAS ---\n"
    productos = list(productos)
    if productos:
        for producto in productos:
            categoria = producto.codigo_categoria
            marca = producto.codigo_marca
            detalle = producto.codigo_detalle_producto
            if detalle:
                existencias = (
                    f"{detalle.cantidad_actual} unidades "
                    f"(mínimo: {detalle.stock_min}, máximo: {detalle.stock_max})"
                )
            else:
                existencias = "sin registro de existencias"

            contexto += (
                f"- {producto.nombre} | Precio de venta: "
                f"${producto.precio_venta_contexto:.0f} | "
                f"Categoría: {categoria.nombre if categoria else 'Sin categoría'} | "
                f"Marca: {marca.nombre if marca else 'Sin marca'} | "
                f"Existencias: {existencias} | "
                f"Estado: {'Activo' if producto.estado else 'Inactivo'}\n"
            )
    else:
        contexto += "- No hay productos registrados.\n"

    contexto += "\n--- CATEGORÍAS REGISTRADAS ---\n"
    categorias = list(categorias)
    if categorias:
        for categoria in categorias:
            contexto += f"- {categoria.nombre}\n"
    else:
        contexto += "- No hay categorías registradas.\n"

    contexto += "\n--- MARCAS REGISTRADAS ---\n"
    marcas = list(marcas)
    if marcas:
        for marca in marcas:
            estado = "Activa" if marca.estado else "Inactiva"
            contexto += f"- {marca.nombre} | Estado: {estado}\n"
    else:
        contexto += "- No hay marcas registradas.\n"

    contexto += "\n--- SERVICIOS REGISTRADOS ---\n"
    servicios = list(servicios)
    if servicios:
        for servicio in servicios:
            contexto += (
                f"- {servicio.nombre}: ${servicio.precio:.0f} | "
                f"Duración: {servicio.duracion} min | "
                f"Estado: {'Activo' if servicio.estado else 'Inactivo'}\n"
            )
    else:
        contexto += "- No hay servicios registrados.\n"

    contexto += "\n--- PROMOCIONES REGISTRADAS ---\n"
    promociones = list(promociones)
    if promociones:
        hoy = timezone.localdate()
        for promocion in promociones:
            destinos = []
            if promocion.codigo_servicio:
                destinos.append(f"servicio {promocion.codigo_servicio.nombre}")
            if promocion.codigo_producto:
                destinos.append(f"producto {promocion.codigo_producto.nombre}")
            destino = ", ".join(destinos) if destinos else "sin producto o servicio asociado"
            vigencia = (
                "vigente por fechas"
                if promocion.fecha_inicio <= hoy <= promocion.fecha_fin
                else "fuera del rango de fechas"
            )
            contexto += (
                f"- {promocion.nombre}: {promocion.porcentaje_descuento}% de descuento "
                f"en {destino} | Fechas: {promocion.fecha_inicio} a "
                f"{promocion.fecha_fin} | Estado: "
                f"{'Activa' if promocion.estado else 'Inactiva'}, {vigencia}\n"
            )
    else:
        contexto += "- No hay promociones registradas.\n"

    return contexto

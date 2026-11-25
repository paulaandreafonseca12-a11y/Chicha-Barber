from django.http import JsonResponse
from chat_ia.ai_service import obtener_respuesta_ia
from chat_ia.contexto_adm import obtener_contexto_admin
from servicios.models import Servicios
from catalogo.models import Producto, Categoria, Promocion
from usuarios.models import RolUsuario

MENSAJE_BIENVENIDA = "¡Hola! 👋 Soy **ChichaBot**, tu asistente virtual de **Chicha Barber Studio**.\n\nEstoy aquí para ayudarte con:\n• 📅 Agendar citas\n• 🛒 ventar productos\n• 💇 Servicios disponibles\n• ❓ Cualquier duda sobre la barbería\n\n¿En qué puedo ayudarte hoy?"


def construir_contexto_dinamico():
    """Construye un contexto con datos reales de la BD para que la IA responda con info actualizada."""
    servicios = Servicios.objects.filter(estado=True)
    promociones = Promocion.objects.filter(estado=True)
    categorias = Categoria.objects.all()
    productos = Producto.objects.filter(estado=True)

    contexto_extra = "=== DATOS ACTUALES DEL SISTEMA (información real) ===\n\n"

    contexto_extra += "--- SERVICIOS DISPONIBLES ---\n"
    if servicios.exists():
        for s in servicios:
            contexto_extra += f"- {s.nombre}: ${s.precio:.0f} | Duración: {s.duracion} min | {s.descripcion}\n"
    else:
        contexto_extra += "- No hay servicios registrados actualmente.\n"

    contexto_extra += "\n--- PROMOCIONES VIGENTES ---\n"
    if promociones.exists():
        for p in promociones:
            if p.codigo_servicio:
                destino = f"el servicio {p.codigo_servicio.nombre}"
            elif p.codigo_producto:
                destino = f"el producto {p.codigo_producto.nombre}"
            else:
                destino = "servicios o productos"

            contexto_extra += f"- {p.nombre}: {p.porcentaje_descuento}% de descuento en {destino} | {p.descripcion}\n"
    else:
        contexto_extra += "- No hay promociones activas en este momento.\n"

    contexto_extra += "\n--- CATEGORÍAS DE PRODUCTOS ---\n"
    if categorias.exists():
        for c in categorias:
            contexto_extra += f"- {c.nombre}: {c.descripcion or 'Sin descripción'}\n"
    else:
        contexto_extra += "- No hay categorías registradas.\n"

    contexto_extra += "\n--- PRODUCTOS EN VENTA ---\n"
    if productos.exists():
        for p in productos:
            categoria = getattr(p, 'codigo_categoria', None)
            contexto_extra += (
                f"- {p.nombre} | Precio: ${p.precio:.0f} | "
                f"Categoría: {categoria.nombre if categoria else 'Sin categoría'} | "
                f"Estado: {'Activo' if p.estado else 'Inactivo'}\n"
            )
    else:
        contexto_extra += "- No hay productos disponibles actualmente.\n"

    return contexto_extra


MENSAJE_BIENVENIDA_ADMIN = (
    "¡Hola! Soy ChichaBot, tu asistente para la gestión del panel administrativo. "
    "Puedo orientarte sobre inventario, productos, servicios, ventas y reservas."
)


def _procesar_chat(request, clave_sesion, mensaje_bienvenida, constructor_contexto, es_admin=False):
    if clave_sesion not in request.session:
        request.session[clave_sesion] = []
        request.session[clave_sesion].append({"rol": "ia", "texto": mensaje_bienvenida})
        request.session.modified = True

    if request.method == "POST":
        user_input = request.POST.get("pregunta")
        if user_input:
            chat = request.session[clave_sesion]
            # Agregar mensaje usuario
            chat.append({"rol": "user", "texto": user_input})
            
            contexto = constructor_contexto()
            if es_admin:
                respuesta = obtener_respuesta_ia(
                    user_input,
                    system_prompt_base=contexto,
                )
            else:
                respuesta = obtener_respuesta_ia(
                    user_input,
                    system_prompt_extra=contexto,
                )
            
            # Agregar mensaje IA
            chat.append({"rol": "ia", "texto": respuesta})
            
            request.session[clave_sesion] = chat
            request.session.modified = True
            
            return JsonResponse({"status": "ok", "nuevo_mensaje": respuesta})

    return JsonResponse({"chat": request.session[clave_sesion]})


def vista_chat_ia(request):
    return _procesar_chat(
        request,
        clave_sesion="chat",
        mensaje_bienvenida=MENSAJE_BIENVENIDA,
        constructor_contexto=construir_contexto_dinamico,
    )


def vista_chat_admin(request):
    if (
        not request.user.is_authenticated
        or request.user.rol not in (RolUsuario.ADMIN, RolUsuario.BARBERO)
    ):
        return JsonResponse(
            {"error": "No tienes permiso para usar el asistente administrativo."},
            status=403,
        )

    return _procesar_chat(
        request,
        clave_sesion="chat_admin",
        mensaje_bienvenida=MENSAJE_BIENVENIDA_ADMIN,
        constructor_contexto=obtener_contexto_admin,
        es_admin=True,
    )

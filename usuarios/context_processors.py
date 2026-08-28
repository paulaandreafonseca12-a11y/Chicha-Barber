from usuarios.models import Notificacion


def notificaciones(request):

    if not request.user.is_authenticated:
        return {
            "notificaciones_lista": [],
            "notificaciones_no_leidas": 0,
        }

    # Se cambió "-fecha_creacion" por "-fecha"
    notificaciones_qs = (
        Notificacion.objects
        .filter(usuario=request.user)
        .order_by("-fecha")
    )

    return {
        "notificaciones_lista": notificaciones_qs[:8],
        "notificaciones_no_leidas": notificaciones_qs.filter(
            leida=False
        ).count(),
    }
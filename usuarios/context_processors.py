from .models import Notificacion

def notificaciones(request):
    if request.user.is_authenticated:
        qs = Notificacion.objects.filter(usuario=request.user)
        return {
            'notificaciones_lista': qs[:8],
            'notificaciones_no_leidas': qs.filter(leida=False).count(),
        }
    return {'notificaciones_lista': [], 'notificaciones_no_leidas': 0}
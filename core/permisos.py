from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from usuarios.models import RolUsuario


def _destino_sin_permiso(user):
    """Página segura a la que se devuelve a cada rol cuando no tiene permiso."""
    if user.rol == RolUsuario.ADMIN:
        return 'inicio_admin'
    if user.rol == RolUsuario.BARBERO:
        return 'ver_agenda'
    return 'inicio'


def rol_requerido(*roles):
    """Permite el acceso solo a los roles indicados."""
    def decorador(vista):
        @wraps(vista)
        def envoltura(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if request.user.rol not in roles:
                messages.error(
                    request,
                    'No tienes permiso para acceder a esta sección.'
                )
                return redirect(_destino_sin_permiso(request.user))
            return vista(request, *args, **kwargs)
        return envoltura
    return decorador


solo_admin = rol_requerido(RolUsuario.ADMIN)
admin_o_barbero = rol_requerido(RolUsuario.ADMIN, RolUsuario.BARBERO)
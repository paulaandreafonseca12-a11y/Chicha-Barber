from urllib.parse import urlparse

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, resolve_url
from django.urls import Resolver404, resolve
from django.utils.http import url_has_allowed_host_and_scheme

from core.permisos import _destino_sin_permiso
from usuarios.models import RolUsuario

MENSAJE = 'No tienes permiso para acceder a esta sección.'

# Rutas (por prefijo) que el barbero NO puede abrir.
# OJO: '/panel/' NO va aquí, es la entrada del barbero a su panel.
PREFIJOS_BLOQUEADOS_BARBERO = (
    '/compras/',
    '/historial/',
    '/configuracion/',
    '/usuarios/lista/',
    '/usuarios/crear/',
    '/usuarios/editar/',
    '/usuarios/eliminar/',
    '/reservas/agenda/crear/',
    '/reservas/gestion-dias/',
    '/servicios/listado/',
)

# Rutas (por nombre, el name= del urls.py) que el barbero NO puede abrir.
# Sirve para apps que mezclan rutas de admin y públicas.
NOMBRES_BLOQUEADOS_BARBERO = {
    # Servicios
    'crear_servicios',
    'editar-servicios',
    'eliminar-servicios',
    # Promociones
    'crear_promocion',
    'editar-promocion',
    'eliminar-promocion',
    # Calificaciones
    'responder-calificacion',
    'eliminar_calificacion',
    # TODO: agregar aquí el name del listado de promociones
    # y el del listado de calificaciones.
}

# Páginas que nunca se usan como "volver a la página anterior".
PREFIJOS_SIN_RETORNO = (
    '/login/',
    '/logout/',
    '/recuperar',
)


def _es_ajax(request):
    return (
        request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or 'application/json' in request.headers.get('accept', '')
    )


def _bloqueada_para_barbero(path):
    """True si esa ruta está vetada al barbero (por prefijo o por nombre)."""
    if path.startswith(PREFIJOS_BLOQUEADOS_BARBERO):
        return True
    try:
        nombre = resolve(path).url_name
    except Resolver404:
        return False
    return nombre in NOMBRES_BLOQUEADOS_BARBERO


class PermisosPorRolMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        # 1) Rutas bloqueadas (solo barbero)
        if (
            user.is_authenticated
            and user.rol == RolUsuario.BARBERO
            and _bloqueada_para_barbero(request.path)
        ):
            return self._denegar(request)

        response = self.get_response(request)

        # 2) Cualquier 403 (lanzado o devuelto) se convierte en el
        #    mensaje dentro del panel.
        if (
            response.status_code == 403
            and user.is_authenticated
            and not _es_ajax(request)
        ):
            return self._denegar(request, original=response)

        return response

    def process_exception(self, request, exception):
        # Convierte los PermissionDenied lanzados en cualquier vista.
        if (
            isinstance(exception, PermissionDenied)
            and request.user.is_authenticated
            and not _es_ajax(request)
        ):
            return self._denegar(request)
        return None

    def _denegar(self, request, original=None):
        destino = self._destino(request)

        # Evita un bucle: si el destino es la misma página, no redirigir.
        try:
            if resolve_url(destino).split('?')[0] == request.path:
                return original if original is not None else redirect('/')
        except Exception:
            pass

        messages.error(request, MENSAJE)
        return redirect(destino)

    def _destino(self, request):
        # Si venía de otra página permitida, lo devuelve ahí.
        referer = request.META.get('HTTP_REFERER', '')
        if referer and url_has_allowed_host_and_scheme(
            referer, allowed_hosts={request.get_host()}
        ):
            ruta = urlparse(referer).path
            es_barbero = request.user.rol == RolUsuario.BARBERO
            if (
                ruta != request.path
                and not ruta.startswith(PREFIJOS_SIN_RETORNO)
                and not (es_barbero and _bloqueada_para_barbero(ruta))
            ):
                return referer
        return _destino_sin_permiso(request.user)
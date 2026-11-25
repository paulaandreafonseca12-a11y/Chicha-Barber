from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from usuarios.models import RolUsuario


def admin_required(view_func):
    @login_required
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if getattr(request.user, "rol", None) != RolUsuario.ADMIN:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapped_view

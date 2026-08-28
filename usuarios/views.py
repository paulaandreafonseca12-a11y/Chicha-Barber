from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

import re

from .models import (
    Usuario,
    RegistroActividad,
    Notificacion,
    RolUsuario,
)

from .forms import (
    RegistroForm,
    CustomLoginForm,
    CrearUsuarioAdminForm,
    EditarUsuarioForm,
    EditarPerfilForm,
    RecuperarPasswordForm,
)

from core.utils import enviar_correo_recuperacion
from core.validators import validar_password_fuerte

from reservas.models import Reserva
from venta.models import Venta


# ==========================================================
# INICIO
# ==========================================================

def inicio(request):

    context = {
        'titulo': 'Inicio',
        'usuario': request.user,
    }

    return render(
        request,
        'index.html',
        context
    )


# ==========================================================
# LOGIN
# ==========================================================

def login_view(request):

    next_url = (
        request.GET.get('next')
        or request.POST.get('next')
        or ''
    )

    if request.user.is_authenticated:
        return redirect('inicio')

    if request.method == 'POST':

        form = CustomLoginForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            messages.success(
                request,
                f"¡Bienvenido de nuevo, {user.primer_nombre}!"
            )

            if next_url:
                return redirect(next_url)

            return redirect('inicio')

        messages.error(
            request,
            "❌ Correo o contraseña incorrectos. "
            "Por favor, verifica los datos."
        )

    else:

        form = CustomLoginForm()

    context = {
        'form': form,
        'text': next_url,
        'titulo': 'Iniciar Sesión',
    }

    return render(
        request,
        'registration/login.html',
        context
    )


# ==========================================================
# REGISTRO
# ==========================================================

def registro_view(request):

    next_url = (
        request.GET.get('next')
        or request.POST.get('next')
        or ''
    )

    if request.method == 'POST':

        form = RegistroForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            # Todos los usuarios que se registran
            # desde el formulario son clientes.
            user.rol = RolUsuario.CLIENTE
            user.estado = True

            user.save()

            # Registrar la acción
            RegistroActividad.objects.create(
                usuario=user,
                tipo='usuario',
                descripcion='Creó su cuenta'
            )

            login(request, user)

            messages.success(
                request,
                "✅ ¡Usuario registrado con éxito! "
                "Tu sesión ha sido iniciada."
            )

            if next_url:
                return redirect(next_url)

            return redirect('inicio')

    else:

        form = RegistroForm()

    context = {
        'form': form,
        'next': next_url,
        'titulo': 'Registro',
    }

    return render(
        request,
        'usuarios/registro.html',
        context
    )


# ==========================================================
# LISTA DE USUARIOS
# ==========================================================

@login_required
def lista_usuarios(request):

    rol_filtro = request.GET.get('rol')

    if rol_filtro:

        usuarios = Usuario.objects.filter(
            rol=rol_filtro
        )

    else:

        usuarios = Usuario.objects.all()

    usuarios = usuarios.order_by(
        'primer_nombre',
        'primer_apellido'
    )

    context = {

        'usuarios': usuarios,

        'titulo': (
            rol_filtro.capitalize()
            if rol_filtro
            else 'Todos los Usuarios'
        ),

        'total_usuarios': Usuario.objects.count(),

        'total_clientes': Usuario.objects.filter(
            rol=RolUsuario.CLIENTE
        ).count(),

        'total_barberos': Usuario.objects.filter(
            rol=RolUsuario.BARBERO
        ).count(),

        'total_admins': Usuario.objects.filter(
            rol=RolUsuario.ADMIN
        ).count(),

        'rol_filtro': rol_filtro,
    }

    return render(
        request,
        'usuarios/lista_usuarios.html',
        context
    )


# ==========================================================
# CREAR USUARIO DESDE ADMIN
# ==========================================================

@login_required
def crear_usuario_admin(request):

    if request.user.rol != RolUsuario.ADMIN:

        messages.error(
            request,
            "❌ Acceso denegado. "
            "Solo un administrador puede crear usuarios."
        )

        return redirect('lista_usuarios')

    if request.method == 'POST':

        form = CrearUsuarioAdminForm(request.POST)

        if form.is_valid():

            user = form.save(commit=False)

            user.rol = form.cleaned_data['rol']

            user.estado = form.cleaned_data.get(
                'estado',
                True
            )

            user.save()

            RegistroActividad.objects.create(
                usuario=request.user,
                tipo='usuario',
                descripcion=(
                    f'Creó el usuario '
                    f'"{user.get_full_name()}" '
                    f'con rol '
                    f'{user.get_rol_display()}'
                )
            )

            messages.success(
                request,
                "✅ Usuario creado con éxito."
            )

            return redirect('lista_usuarios')

    else:

        form = CrearUsuarioAdminForm()

    context = {
        'form': form,
        'titulo': 'Crear Usuario',
    }

    return render(
        request,
        'usuarios/crear_usuario.html',
        context
    )


# ==========================================================
# CAMBIAR TEMA
# ==========================================================
#
# IMPORTANTE:
# Tu modelo Usuario actual NO tiene campo "tema".
# Por eso no intentamos guardar user.tema.
# ==========================================================

@login_required
def cambiar_tema(request):

    return redirect(
        request.META.get(
            'HTTP_REFERER',
            'inicio'
        )
    )


# ==========================================================
# EDITAR USUARIO
# ==========================================================

@login_required
def editar_usuario(request, pk):

    if request.user.rol != RolUsuario.ADMIN:

        messages.error(
            request,
            "❌ Acceso denegado. "
            "Solo un administrador puede editar usuarios."
        )

        return redirect('lista_usuarios')

    usuario = get_object_or_404(
        Usuario,
        pk=pk
    )

    if request.method == 'POST':

        form = EditarUsuarioForm(
            request.POST,
            request.FILES,
            instance=usuario
        )

        if form.is_valid():

            form.save()

            RegistroActividad.objects.create(
                usuario=request.user,
                tipo='usuario',
                descripcion=(
                    f'Editó el usuario '
                    f'"{usuario.get_full_name()}"'
                )
            )

            messages.success(
                request,
                f"✅ Usuario "
                f"{usuario.get_full_name()} "
                f"actualizado con éxito."
            )

            return redirect('lista_usuarios')

    else:

        form = EditarUsuarioForm(
            instance=usuario
        )

    context = {
        'form': form,
        'usuario': usuario,
        'titulo': 'Editar Usuario',
    }

    return render(
        request,
        'usuarios/editar_usuario.html',
        context
    )


# ==========================================================
# RECUPERAR CONTRASEÑA
# ==========================================================

def recuperar_password_view(request):

    if request.method == 'POST':

        form = RecuperarPasswordForm(
            request.POST
        )

        if form.is_valid():

            email = form.cleaned_data['email']

            try:

                usuario = Usuario.objects.get(
                    email__iexact=email
                )

            except Usuario.DoesNotExist:

                messages.error(
                    request,
                    "❌ No existe una cuenta registrada "
                    "con ese correo."
                )

                context = {
                    'form': form,
                    'titulo': 'Recuperar Contraseña',
                }

                return render(
                    request,
                    'registration/recuperar.html',
                    context
                )

            uid = urlsafe_base64_encode(
                force_bytes(usuario.pk)
            )

            token = default_token_generator.make_token(
                usuario
            )

            reset_url = request.build_absolute_uri(
                f'/recuperar/{uid}/{token}/'
            )

            try:

                enviar_correo_recuperacion(
                    correo_cliente=usuario.email,
                    nombre=usuario.primer_nombre,
                    reset_url=reset_url
                )

            except Exception:

                messages.error(
                    request,
                    "❌ No se pudo enviar el correo "
                    "de recuperación. "
                    "Intenta nuevamente."
                )

                context = {
                    'form': form,
                    'titulo': 'Recuperar Contraseña',
                }

                return render(
                    request,
                    'registration/recuperar.html',
                    context
                )

            return redirect(
                'password_reset_done'
            )

    else:

        form = RecuperarPasswordForm()

    context = {
        'form': form,
        'titulo': 'Recuperar Contraseña',
    }

    return render(
        request,
        'registration/recuperar.html',
        context
    )


# ==========================================================
# PERFIL
# ==========================================================

@login_required
def perfil(request):

    form = EditarPerfilForm(
        instance=request.user
    )

    # ------------------------------------------------------
    # EDITAR PERFIL
    # ------------------------------------------------------

    if request.method == 'POST':

        if 'editar_perfil' in request.POST:

            form = EditarPerfilForm(
                request.POST,
                request.FILES,
                instance=request.user
            )

            if form.is_valid():

                form.save()

                RegistroActividad.objects.create(
                    usuario=request.user,
                    tipo='usuario',
                    descripcion='Actualizó su perfil'
                )

                messages.success(
                    request,
                    "✅ Perfil actualizado con éxito."
                )

                return redirect('perfil')

            else:

                messages.error(
                    request,
                    "❌ Revisa los datos del formulario, "
                    "hay errores."
                )

        # --------------------------------------------------
        # CAMBIAR CONTRASEÑA
        # --------------------------------------------------

        elif 'cambiar_password' in request.POST:

            actual = request.POST.get(
                'password_actual',
                ''
            )

            nueva = request.POST.get(
                'password_nueva',
                ''
            )

            confirmar = request.POST.get(
                'password_confirmar',
                ''
            )

            if not request.user.check_password(actual):

                messages.error(
                    request,
                    "❌ La contraseña actual es incorrecta."
                )

            elif nueva != confirmar:

                messages.error(
                    request,
                    "❌ Las contraseñas nuevas no coinciden."
                )

            else:

                try:

                    validar_password_fuerte(
                        nueva
                    )

                    request.user.set_password(
                        nueva
                    )

                    request.user.save()

                    update_session_auth_hash(
                        request,
                        request.user
                    )

                    RegistroActividad.objects.create(
                        usuario=request.user,
                        tipo='sesion',
                        descripcion='Cambió su contraseña'
                    )

                    messages.success(
                        request,
                        "✅ Contraseña actualizada."
                    )

                    return redirect('perfil')

                except ValidationError as e:

                    for error in e.messages:

                        messages.error(
                            request,
                            f"❌ {error}"
                        )

    # ======================================================
    # HISTORIAL DEL PERFIL
    # ======================================================
    #
    # IMPORTANTE:
    # AQUÍ NO USAMOS HistorialAccion.
    #
    # El historial de acciones del sistema se maneja con
    # RegistroActividad dentro de usuarios.
    #
    # RegistroActividad utiliza el campo "fecha".
    # ======================================================

    actividades = RegistroActividad.objects.all().order_by(
        '-fecha'
    )[:20]

    # ======================================================
    # RESERVAS DEL USUARIO
    # ======================================================

    reservas = Reserva.objects.filter(
        cliente=request.user
    ).order_by(
        '-fecha_reserva'
    )

    # ======================================================
    # VENTAS DEL USUARIO
    # ======================================================

    ventas = Venta.objects.filter(
        correo=request.user.email
    ).order_by(
        '-fecha'
    )

    # ======================================================
    # CONTEXTO
    # ======================================================

    context = {

        'form': form,

        'reservas': reservas,

        'ventas': ventas,

        # Historial de acciones
        'actividades': actividades,

    }

    return render(
        request,
        'private/perfil.html',
        context
    )


# ==========================================================
# MARCAR NOTIFICACIONES COMO LEÍDAS
# ==========================================================

@login_required
def marcar_notificaciones_leidas(request):

    Notificacion.objects.filter(
        usuario=request.user,
        leida=False
    ).update(
        leida=True
    )

    return redirect(
        request.META.get(
            'HTTP_REFERER',
            'inicio'
        )
    )


# ==========================================================
# DETALLE DE NOTIFICACIÓN
# ==========================================================

@login_required
def detalle_notificacion(request, pk):

    notificacion = get_object_or_404(
        Notificacion,
        pk=pk,
        usuario=request.user
    )

    if not notificacion.leida:

        notificacion.leida = True

        notificacion.save()

    match = re.search(
        r'#(\d+)',
        notificacion.mensaje
    )

    rel_id = (
        match.group(1)
        if match
        else None
    )

    # ------------------------------------------------------
    # ADMIN / BARBERO
    # ------------------------------------------------------

    if request.user.rol in (
        RolUsuario.ADMIN,
        RolUsuario.BARBERO
    ):

        if notificacion.tipo == 'reserva':

            return redirect(
                'ver_agenda'
            )

        elif notificacion.tipo == 'venta':

            if rel_id:

                try:

                    Venta.objects.get(
                        pk=rel_id
                    )

                    return redirect(
                        'detalle_venta',
                        pk=rel_id
                    )

                except Venta.DoesNotExist:

                    pass

            return redirect(
                'historial_ventas'
            )

    # ------------------------------------------------------
    # CLIENTE
    # ------------------------------------------------------

    objeto_relacionado = None

    if rel_id:

        try:

            if notificacion.tipo == 'venta':

                objeto_relacionado = Venta.objects.get(
                    pk=rel_id,
                    correo=request.user.email
                )

            elif notificacion.tipo == 'reserva':

                objeto_relacionado = Reserva.objects.get(
                    pk=rel_id,
                    cliente=request.user
                )

        except (
            Venta.DoesNotExist,
            Reserva.DoesNotExist
        ):

            objeto_relacionado = None

    context = {

        'notificacion': notificacion,

        'objeto_relacionado': objeto_relacionado,

        'titulo': 'Detalle de Notificación',

    }

    return render(
        request,
        'private/detalle_notificacion.html',
        context
    )
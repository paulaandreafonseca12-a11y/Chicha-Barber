from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import login as auth_login  # 🔥 IMPORTANTE: Para loguear automáticamente
from .forms import RegistroForm
from .models import Usuario
from .forms import RegistroForm, CrearUsuarioAdminForm
from .forms import RegistroForm, CrearUsuarioAdminForm, EditarUsuarioForm
from django.shortcuts import get_object_or_404

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from core.utils import enviar_correo_recuperacion

def inicio(request):
    return render(request, 'index.html')


def registro_view(request):
    # Capturamos la URL a la que el usuario quería ir originalmente
    next_url = request.GET.get('next') or request.POST.get('next') or ''

    if request.method == 'POST':
        form = RegistroForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)

            # 🔥 FIJO: todos son cliente
            user.rol = "cliente"

            # Seguridad extra
            user.is_staff = False
            user.is_superuser = False

            user.save()

            # 🔥 NUEVO: Iniciamos sesión automáticamente para evitar que pase por el login manual
            auth_login(request, user)

            messages.success(
                request,
                "✅ ¡Usuario registrado con éxito! Tu sesión ha sido iniciada."
            )

            # 🔥 MEJORA: Si venía de una reserva, va directo a procesarla en reservas/views.py
            if next_url:
                return redirect(next_url)
            
            return redirect('inicio') 

    else:
        form = RegistroForm()

    return render(request, 'usuarios/registro.html', {
        'form': form,
        'next': next_url # Pasamos 'next' al template
    })


def lista_usuarios(request):
    rol_filtro = request.GET.get('rol')

    if rol_filtro:
        usuarios = Usuario.objects.filter(rol=rol_filtro)
    else:
        usuarios = Usuario.objects.all()

    usuarios = usuarios.order_by('first_name', 'last_name')

    return render(request, 'usuarios/lista_usuarios.html', {
        'usuarios': usuarios,
        'titulo': rol_filtro.capitalize() if rol_filtro else "Todos los Usuarios"
    })



def crear_usuario_admin(request):
    if request.method == 'POST':
        form = CrearUsuarioAdminForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.rol = form.cleaned_data['rol']
            user.is_staff = form.cleaned_data.get('is_staff', False)
            user.is_superuser = False
            user.save()
            messages.success(request, "✅ Usuario creado con éxito.")
            return redirect('lista_usuarios')
    else:
        form = CrearUsuarioAdminForm()

    return render(request, 'usuarios/crear_usuario.html', {'form': form})

def perfil(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado con éxito.")
            return redirect('perfil')
    else:
        form = RegistroForm(instance=request.user)
        
    return render(request, 'private/perfil.html')


def cambiar_tema(request):
    if not request.user.is_authenticated:
        return redirect('login')
    user = request.user
    user.tema = 'dark' if getattr(user, 'tema', 'light') == 'light' else 'light'
    user.save()
    return redirect(request.META.get('HTTP_REFERER', 'inicio'))

def editar_usuario(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = EditarUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ Usuario {usuario.get_full_name()} actualizado con éxito.")
            return redirect('lista_usuarios')
    else:
        form = EditarUsuarioForm(instance=usuario)

    return render(request, 'usuarios/editar_usuario.html', {
        'form': form,
        'usuario': usuario
    })
    


def recuperar_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            usuario = Usuario.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))
            token = default_token_generator.make_token(usuario)
            reset_url = request.build_absolute_uri(
                f'/recuperar/{uid}/{token}/'
            )
            enviar_correo_recuperacion(
                correo_cliente=usuario.email,
                nombre=usuario.first_name,
                reset_url=reset_url
            )
        except Usuario.DoesNotExist:
            pass
        except Exception:
            pass  # No revelar si el correo existe o no

        return redirect('password_reset_done')

    return render(request, 'registration/recuperar.html')

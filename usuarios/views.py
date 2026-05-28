from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from django.contrib.auth import login as auth_login  # 🔥 IMPORTANTE: Para loguear automáticamente
from .forms import RegistroForm
from .models import Usuario


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
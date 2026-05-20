from django.shortcuts import render, redirect, reverse
from django.contrib import messages
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

            messages.success(
                request,
                "✅ Usuario registrado como cliente con éxito."
            )

            # Si existe una URL de destino, la pasamos al login
            if next_url:
                return redirect(f"{reverse('login')}?next={next_url}")
            
            return redirect('login') 

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
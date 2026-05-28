from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import RegistroForm
from .models import Usuario
from .forms import RegistroForm, CrearUsuarioAdminForm

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
    user = request.user
    user.tema = 'dark' if getattr(user, 'tema', 'light') == 'light' else 'light'
    user.save()
    return redirect(request.META.get('HTTP_REFERER', 'inicio'))
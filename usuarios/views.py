from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import RegistroForm
from .models import Usuario

def inicio(request):
    return render(request, 'index.html')

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            # .save() en un UserCreationForm ya maneja el cifrado de contraseña
            user = form.save(commit=False)
            user.rol = form.cleaned_data.get('rol')
            
            # Lógica de permisos automática
            if user.rol == 'barbero':
                user.is_staff = True
            
            user.save()
            messages.success(request, f"✅ {user.get_rol_display()} registrado con éxito.")
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def lista_usuarios(request):
    # Capturamos el rol de la URL (ej: /usuarios/?rol=barbero)
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
    
   
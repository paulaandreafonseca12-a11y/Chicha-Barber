from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import RegistroForm
from .models import Usuario

def inicio(request):
    return render(request, 'index.html')

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password1'])
            user.rol = form.cleaned_data['rol']
            # Si es barbero, darle acceso al admin
            if user.rol == 'barbero':
                user.is_staff = True
            user.save()
            messages.success(request, "✅ Usuario registrado correctamente.")
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})

def login_view(request):
    return render(request, 'registration/login.html')

def lista_clientes(request):
    clientes = Usuario.objects.filter(rol='cliente').order_by('nombre_completo')
    return render(request, 'usuarios/clientes.html', {'clientes': clientes})

def lista_barberos(request):
    barberos = Usuario.objects.filter(rol='barbero').order_by('nombre_completo')
    return render(request, 'usuarios/barberos.html', {'barberos': barberos})
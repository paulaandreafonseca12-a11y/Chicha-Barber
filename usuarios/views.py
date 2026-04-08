from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistroForm


def inicio(request):
    
    return render(request, 'index.html')

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Usamos el email como nombre de usuario para que no pida uno extra
            user.username = form.cleaned_data['email']
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return redirect('login') # O a donde quieras smandarlo
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})
# Agrega esta también si la estás llamando en las URLs
def login_view(request):
    return render(request, 'registration/login.html')
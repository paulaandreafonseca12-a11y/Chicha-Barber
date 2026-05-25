from multiprocessing import context
from django.contrib import messages  # type: ignore


from django.shortcuts import render,redirect, get_object_or_404 # type: ignore
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


from servicios.forms import ServiciosEditarForm, ServiciosForm, PromocionForm
from servicios.models import Promocion
from usuarios.forms import CustomLoginForm

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    form_class = CustomLoginForm
    
    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        # Redirigir al panel si es administrador, de lo contrario al inicio
        if self.request.user.rol == 'admin':
            return reverse_lazy('inicio_admin')
        return reverse_lazy('inicio')

from configuraciones.models import Carrusel

def inicio(request):
    carruseles = Carrusel.objects.filter(estado=True).order_by('-fecha_modificacion')[:4]
    nombre = "Santiago"
    context = {
        'nombre': nombre,
        'carruseles': carruseles,
    }
    return render(request, 'index-clientes.html', context)

def inicio_admin(request):
    nombre = "Santiago"
    context = {
        'nombre': nombre
    }
    return render(request, 'index-admin.html', context)


def crear_promocion(request):
    if request.method == 'POST':
        form = PromocionForm(request.POST, request.FILES)
        if form.is_valid():
            promocion = form.save()
            messages.success(request, 'Promoción creada exitosamente.')
            return redirect('crear_promocion')
        else:
            messages.error(request, 'Error al crear la promoción. Por favor, inténtalo de nuevo.')
            
            
  

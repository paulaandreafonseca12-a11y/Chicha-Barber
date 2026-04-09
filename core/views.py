from multiprocessing import context
from django.contrib import messages  # type: ignore


from django.shortcuts import render,redirect, get_object_or_404 # type: ignore



from servicios.forms import ServiciosEditarForm, ServiciosForm
from servicios.models import Promocion

def inicio(request):
    nombre = "Santiago"
    context = {
        'nombre': nombre
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
        # Aquí puedes manejar la lógica para crear una promocion con los datos del formulario
        form = Promocion(request.POST)
        if form.is_valid():
            promocion = form.save()
            messages.success(request, 'Promoción creada exitosamente.')
            return redirect('crear_promocion')
        else:
            messages.error(request, 'Error al crear la promoción. Por favor, inténtalo de nuevo.')
            
            
  





# Create your views here.

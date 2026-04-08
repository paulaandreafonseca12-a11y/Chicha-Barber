from django.shortcuts import render # type: ignore
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib import messages # type: ignore
from .models import *
from .forms import serviciosForm, serviciosEditarForm

def servicios_view(request):
    servicios = Servicios.objects.all()
    
    context = {
        'titulo': 'Nuestros Servicios',
        'servicios': servicios
    }
    return render(request, 'servicios.html', context)
def servicios_admin_view(request):
    servicios = Servicios.objects.all()
    context = {
        'titulo': 'Nuestros Servicios',
        'servicios': servicios
    }
    return render(request, 'servicios.html', context)

def calificacion_views(request):
    context = {
        'titulo': 'Calificación de Servicios',
    }
    return render(request, 'calificacion.html', context)

def crear_servicios(request):
    if request.method == 'POST':
        form = serviciosForm(request.POST)
        if form.is_valid():
            servicio = form.save(commit=False)
            
            # 1. Asignar el documento como nombre de usuario
            servicio.username = servicio.documento
            
            
            
            # 4. Ahora sí guardamos en la base de datos
            servicio.save()
        else:
            messages.error(request, "Error al crear el servicio. Revisa los campos marcados en rojo.")
    else:
        form = serviciosForm()
    
    context={
        'form': form,
        'titulo': 'Crear nuevo servicio',
    }
    return render(request, 'servicios/agregar_servicio.html', context)


def editar_servicios(request, pk):
    servicio = get_object_or_404(Servicios, pk=pk)

    if request.method == 'POST':
        form = serviciosEditarForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, f"Datos de {servicio.first_name} actualizados correctamente.")
            return redirect('servicios:inicio_servicios')
        else:
            messages.error(request, "Error al actualizar. Revisa los campos marcados en rojo.")
    else:
        form = serviciosEditarForm(instance=servicio)

    context = {
        'form': form,
        'titulo': f'Editar a {servicio.first_name}',
    }
    return render(request, 'servicios/agregar_servicio.html', context)



# Create your views here.


def promocion_views(request):
    context = {
    'titulo' : 'Promociones'
    }
    return render(request, 'promocion.html', context)

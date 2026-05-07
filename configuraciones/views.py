from django.shortcuts import render, redirect # type: ignore
from django.contrib import messages


from .models import Carrusel
from .forms import CarruselForm
from configuraciones import forms

def carrusel_view(request):
    carruseles = Carrusel.objects.all()

    context = {
        'titulo': 'Gestión de Carrusel',
        'carruseles': carruseles,
        
    }
    return render(request, 'carrusel.html', context)

def crear_carrusel(request):
    if request.method == 'POST':
        form = CarruselForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Imagen de carrusel creada exitosamente.')
            return redirect('carrusel'),
    else:
        form = CarruselForm()
    
    return render(request, 'crear_carrusel.html', {'form': form})

def eliminar_carrusel(request, pk):
    try:
        carrusel = Carrusel.objects.get(pk=pk)
        carrusel.delete()
        messages.success(request, 'Imagen de carrusel eliminada exitosamente.')
    except Carrusel.DoesNotExist:
        messages.error(request, 'La imagen de carrusel no existe.')
    return redirect('carrusel')

def editar_carrusel(request, pk):
    try:
        carrusel = Carrusel.objects.get(pk=pk)
    except Carrusel.DoesNotExist:
        messages.error(request, 'La imagen de carrusel no existe.')
        return redirect('carrusel')

    if request.method == 'POST':
        form = CarruselForm(request.POST, request.FILES, instance=carrusel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Imagen de carrusel actualizada exitosamente.')
            return redirect('carrusel')
    else:
        form = CarruselForm(instance=carrusel)
    
    return render(request, 'editar_carrusel.html', {'form': form, 'carrusel': carrusel})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Carrusel
from .forms import CarruselForm

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
            return redirect('carrusel') # Se eliminó la coma extra
    else:
        form = CarruselForm()
    
    return render(request, 'crear_carrusel.html', {'form': form})

def eliminar_carrusel(request, pk):
    # Uso de get_object_or_404 es más limpio y estándar en Django
    try:
        carrusel = Carrusel.objects.get(pk=pk)
        carrusel.delete()
        messages.success(request, 'Imagen de carrusel eliminada exitosamente.')
    except Carrusel.DoesNotExist:
        messages.error(request, 'La imagen de carrusel no existe.')
    return redirect('carrusel')

def editar_carrusel(request, pk):
    # Se optimiza la búsqueda del objeto
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
    
    # Se recomienda pasar 'carrusel' al contexto para mostrar datos en el template (como la imagen actual)
    return render(request, 'editar_carrusel.html', {'form': form, 'carrusel': carrusel})

def toggle_carrusel(request, pk):
    try:
        carrusel = Carrusel.objects.get(pk=pk)
        carrusel.estado = not carrusel.estado
        carrusel.save()
        estado_str = "activado" if carrusel.estado else "inactivado"
        messages.success(request, f'Carrusel {estado_str} exitosamente.')
    except Carrusel.DoesNotExist:
        messages.error(request, 'La imagen de carrusel no existe.')
    return redirect('carrusel')
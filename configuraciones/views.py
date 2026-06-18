from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Carrusel
from .forms import CarruselForm

@login_required
def carrusel_view(request):
    carruseles = Carrusel.objects.all()
    context = {
        'titulo': 'Gestión de Carrusel',
        'carruseles': carruseles,
    }
    return render(request, 'carrusel.html', context)

@login_required
def crear_carrusel(request):
    if request.method == 'POST':
        form = CarruselForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Imagen de carrusel creada exitosamente.')
            return redirect('carrusel') # Se eliminó la coma extra
    else:
        form = CarruselForm()
    
    context = {
        'titulo': 'Crear Carrusel',
        'form': form,
    }
    return render(request, 'crear_carrusel.html', context)

@login_required
def eliminar_carrusel(request, pk):
    carrusel = get_object_or_404(Carrusel, pk=pk)
    carrusel.delete()
    messages.success(request, 'Imagen de carrusel eliminada exitosamente.')
    return redirect('carrusel')

@login_required
def editar_carrusel(request, pk):
    carrusel = get_object_or_404(Carrusel, pk=pk)
    
    if request.method == 'POST':
        form = CarruselForm(request.POST, request.FILES, instance=carrusel)
        if form.is_valid():
            form.save()
            messages.success(request, 'Imagen de carrusel actualizada exitosamente.')
            return redirect('carrusel')
    else:
        form = CarruselForm(instance=carrusel)
    
    context = {
        'titulo': 'Editar Carrusel',
        'form': form,
        'carrusel': carrusel,
    }
    return render(request, 'editar_carrusel.html', context)

@login_required
def toggle_carrusel(request, pk):
    carrusel = get_object_or_404(Carrusel, pk=pk)
    carrusel.estado = not carrusel.estado
    carrusel.save()
    estado_str = "activado" if carrusel.estado else "inactivado"
    messages.success(request, f'Carrusel {estado_str} exitosamente.')
    return redirect('carrusel')

from servicios.models import Calificacion

@login_required
def testimonios_admin_view(request):
    testimonios = Calificacion.objects.filter(puntuacion=5).order_by('-fecha_calificacion')
    context = {
        'titulo': 'Gestión de Testimonios (5 Estrellas)',
        'testimonios': testimonios,
    }
    return render(request, 'testimonios.html', context)

@login_required
def toggle_testimonio(request, pk):
    try:
        testimonio = Calificacion.objects.get(pk=pk, puntuacion=5)
        testimonio.mostrar_en_inicio = not testimonio.mostrar_en_inicio
        testimonio.save()
        estado_str = "aprobado para inicio" if testimonio.mostrar_en_inicio else "ocultado del inicio"
        messages.success(request, f'Testimonio {estado_str} exitosamente.')
    except Calificacion.DoesNotExist:
        messages.error(request, 'El testimonio no existe o no tiene 5 estrellas.')
    return redirect('testimonios_admin')
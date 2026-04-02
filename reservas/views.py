from django.shortcuts import render
from django .shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Reserva, Calificacion
from .forms import ReservaForm, ReservaEditarForm, CalificacionForm, CalificacionEditarForm

# Create your views here.

def reservas_view(request):
    context = {
    'titulo' : 'Reserva el corte que desees'
    }
    return render(request, 'reservas.html', context)

def calificacion_view(request):
    context = {
    'titulo' : 'Califica tu experiencia'
    }
    return render(request, 'calificacion.html', context)

def crear_reserva(request):
    if request.method == 'POST':
        # Aquí puedes manejar la lógica para crear una reserva
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save()
            messages.success(request, 'Reserva creada exitosamente.')
            return redirect('crear_reserva')
        else:
            messages.error(request, 'Error al crear la reserva. Por favor, inténtalo de nuevo.')
    else:
        form = ReservaForm()
        
        context = {
            'form': form,
            'titulo': 'Crear Reserva'
        }
    return render(request, 'reservas/agregar_reserva.html', context)


def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    
    if request.method == 'POST':
        form = ReservaEditarForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva actualizada exitosamente.')
            return redirect('crear_reservas')
        else:
            messages.error(request, 'Error al actualizar la reserva. Por favor, inténtalo de nuevo.')
    else:
        form = ReservaEditarForm(instance=reserva)
        
    context = {
        'form': form,
        'titulo': 'Editar Reserva'
    }
    return render(request, 'reservas/editar_reserva.html', context)


def crear_calificacion(request):
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            calificacion = form.save()
            messages.success(request, 'Calificación creada exitosamente.')
            return redirect('crear_calificacion')
        else:
            messages.error(request, 'Error al crear la calificación. Por favor, inténtalo de nuevo.')
    else:
        form = CalificacionForm()
        
    context = {
        'form': form,
        'titulo': 'Crear Calificación'
    }
    return render(request, 'calificacion/agregar_calificacion.html', context)

def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    
    if request.method == 'POST':
        form = CalificacionEditarForm(request.POST, instance=calificacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Calificación actualizada exitosamente.')
            return redirect('crear_calificacion')
        else:
            messages.error(request, 'Error al actualizar la calificación. Por favor, inténtalo de nuevo.')
    else:
        form = CalificacionEditarForm(instance=calificacion)
        
    context = {
        'form': form,
        'titulo': 'Editar Calificación'
    }
    return render(request, 'calificacion/editar_calificacion.html', context)
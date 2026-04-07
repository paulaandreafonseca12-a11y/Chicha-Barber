from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Reserva, Calificacion
from .forms import ReservaForm, ReservaEditarForm, CalificacionForm, CalificacionEditarForm
from usuarios.models import Barbero 

# --- VISTAS DE RESERVAS ---

def reservas_view(request):
    promo_elegida = request.session.pop('promocion_seleccionada', None)
    context = {
        'promo': promo_elegida,
        'titulo': 'Reserva el corte que desees'
    }
    return render(request, 'reservas/reservas.html', context)

def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        promo_nombre = request.POST.get('promo_oculta') 
        if form.is_valid():
            reserva = form.save()
            mensaje = '¡CITA CONFIRMADA!'
            if promo_nombre:
                mensaje += f' Reservaste con la promoción: {promo_nombre}'
            messages.success(request, mensaje)
            return render(request, 'reservas/confirmacion_exitosa.html', {'promo': promo_nombre})
        else:
            messages.error(request, 'Error al crear la reserva.')
    
    form = ReservaForm()
    return render(request, 'reservas/agregar_reserva.html', {'form': form})

def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        form = ReservaEditarForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva actualizada exitosamente.')
            return redirect('reservas_view')
    else:
        form = ReservaEditarForm(instance=reserva)
    return render(request, 'reservas/editar_reserva.html', {'form': form, 'titulo': 'Editar Reserva'})

# --- VISTAS DE CALIFICACIÓN (LA PARTE QUE FALLABA) ---

def calificacion_view(request):
    """Esta vista maneja la visualización y el envío de reseñas"""
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Gracias por calificar nuestro servicio!')
            return redirect('calificacion_view') 
    else:
        # Aquí se genera el formulario que contiene la lista de barberos
        form = CalificacionForm()
    
    return render(request, 'calificacion.html', {'form': form})

def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    if request.method == 'POST':
        form = CalificacionEditarForm(request.POST, instance=calificacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Calificación actualizada.')
            return redirect('calificacion_view')
    else:
        form = CalificacionEditarForm(instance=calificacion)
    return render(request, 'calificacion/editar_calificacion.html', {'form': form})

# Redirigir a la lista de reservas
    return redirect('reservas_view')
def lista_reservas(request):
    # Traemos todas las reservas de la base de datos
    reservas = Reserva.objects.all().order_by('-fecha_reserva')
    return render(request, 'reservas/lista_reservas.html', {'reservas': reservas})

def cancelar_reserva(request, pk):
    # CB-42: Verificar que la cita exista
    reserva = get_object_or_404(Reserva, pk=pk)
    
    # CB-43: Cambiar el estado de "reservada" a "cancelada"
    reserva.estado = 'cancelada'
    reserva.save()
    
    # CB-44: Mostrar mensaje de confirmación
    messages.success(request, f'La cita de {reserva.nombre_cliente} ha sido cancelada correctamente.')
    
    
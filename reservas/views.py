from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Reserva, Calificacion
from .forms import ReservaForm, ReservaEditarForm, CalificacionForm, CalificacionEditarForm, EditarReservaForm
from usuarios.models import Barbero

# --- VISTAS DE RESERVAS (CLIENTE) ---

def reservas_view(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Cita agendada con éxito!")
            return redirect('reservas:ver_agenda')
        return render(request, 'reservas.html', {'form': form})
    else:
        form = ReservaForm()
        return render(request, 'reservas.html', {'form': form})

def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Cita agendada con éxito!")
            return redirect('reservas:ver_agenda')
        return render(request, 'reservas.html', {'form': form})
    else:
        form = ReservaForm()
        return render(request, 'reservas.html', {'form': form})

def cancelar_cita(request, pk):
    cita = get_object_or_404(Reserva, pk=pk)
    cita.estado = 'cancelada'
    cita.save()
    messages.warning(request, f"La cita de {cita.nombre_cliente} ha sido cancelada.")
    return redirect('reservas:ver_agenda')

# --- VISTAS DE CALIFICACIÓN ---

def calificacion_view(request):
    if request.method == 'POST':
        form = CalificacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Gracias por calificar nuestro servicio!')
            return redirect('reservas:calificacion')
    else:
        form = CalificacionForm()
    return render(request, 'calificacion.html', {'form': form})

def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    if request.method == 'POST':
        form = CalificacionEditarForm(request.POST, instance=calificacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Calificación actualizada.')
            return redirect('reservas:calificacion')
    else:
        form = CalificacionEditarForm(instance=calificacion)
    return render(request, 'calificacion/editar_calificacion.html', {'form': form})

# --- VISTAS DEL ADMINISTRADOR (sin cambios) ---

def ver_agenda(request):
    reservas = Reserva.objects.all().order_by('-fecha_creacion')
    return render(request, 'reservas/ver_agenda.html', {'reservas': reservas})

def cambiar_estado_reserva(request, pk, nuevo_estado):
    reserva = get_object_or_404(Reserva, pk=pk)
    estados_validos = ['reservada', 'confirmada', 'cancelada']
    if nuevo_estado in estados_validos:
        reserva.estado = nuevo_estado
        reserva.save()
        messages.info(request, f"Estado de la cita actualizado a {nuevo_estado}.")
    return redirect('reservas:ver_agenda')

def reprogramar_cita(request, pk):
    cita = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        form = EditarReservaForm(request.POST, instance=cita)
        if form.is_valid():
            form.save()
            messages.success(request, "Cita reprogramada correctamente.")
            return redirect('reservas:ver_agenda')
    else:
        form = EditarReservaForm(instance=cita)
    return render(request, 'reservas/reprogramar.html', {'form': form, 'cita': cita})
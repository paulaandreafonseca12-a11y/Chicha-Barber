from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime

from .models import Reserva, Calificacion
from .forms import (
    ReservaForm,
    ReservaEditarForm,
    CalificacionForm,
    CalificacionEditarForm,
    EditarReservaForm
)

from servicios.models import Servicios


# =========================
# 🔹 RESERVAS (CLIENTE)
# =========================

def reservas_view(request):
    form = ReservaForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "¡Cita agendada con éxito!")
            return redirect('reservas:ver_agenda')

    return render(request, 'reservas.html', {'form': form})


def crear_reserva(request):
    form = ReservaForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "¡Cita agendada con éxito!")
            return redirect('reservas:ver_agenda')

    return render(request, 'reservas.html', {'form': form})


def crear_reserva_user(request, servicio_id):
    servicio = get_object_or_404(Servicios, id=servicio_id)
    form = ReservaForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.servicio = servicio

            fecha_str = request.POST.get('fecha_reserva')

            try:
                reserva.fecha_reserva = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
                reserva.save()
                messages.success(request, f'¡Cita para {servicio.nombre} agendada!')
                return redirect('inicio')
            except (ValueError, TypeError):
                messages.error(request, 'Formato de fecha inválido')

    context = {
        'servicio': servicio,
        'form': form,
        'titulo': f'Agendar {servicio.nombre}'
    }

    return render(request, 'reservas/reservas.html', context)


def cancelar_cita(request, pk):
    cita = get_object_or_404(Reserva, pk=pk)
    cita.estado = 'cancelada'
    cita.save()

    messages.warning(request, f"Cita cancelada: {cita.nombre_cliente}")
    return redirect('reservas:ver_agenda')


def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    form = ReservaEditarForm(request.POST or None, instance=reserva)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva actualizada.')
            return redirect('reservas:ver_agenda')

    return render(request, 'reservas/editar_reserva.html', {
        'form': form,
        'titulo': 'Editar Reserva'
    })


# =========================
# ⭐ CALIFICACIONES
# =========================

def calificacion_view(request):
    form = CalificacionForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, '¡Gracias por calificar!')
            return redirect('reservas:calificacion')

    return render(request, 'calificacion.html', {'form': form})


def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    form = CalificacionEditarForm(request.POST or None, instance=calificacion)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Calificación actualizada.')
            return redirect('reservas:calificacion')

    return render(request, 'calificacion/editar_calificacion.html', {'form': form})


# =========================
# 🔧 ADMIN / AGENDA
# =========================

def ver_agenda(request):
    reservas = Reserva.objects.all().order_by('-fecha_creacion')
    return render(request, 'reservas/ver_agenda.html', {'reservas': reservas})


def cambiar_estado_reserva(request, pk, nuevo_estado):
    reserva = get_object_or_404(Reserva, pk=pk)

    if nuevo_estado in ['reservada', 'confirmada', 'cancelada']:
        reserva.estado = nuevo_estado
        reserva.save()
        messages.info(request, f"Estado actualizado a {nuevo_estado}")

    return redirect('reservas:ver_agenda')


def reprogramar_cita(request, pk):
    cita = get_object_or_404(Reserva, pk=pk)
    form = EditarReservaForm(request.POST or None, instance=cita)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Cita reprogramada")
            return redirect('reservas:ver_agenda')

    return render(request, 'reservas/reprogramar.html', {
        'form': form,
        'cita': cita
    })

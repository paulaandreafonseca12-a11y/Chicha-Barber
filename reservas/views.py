from django.shortcuts import render
from django .shortcuts import render, redirect, get_object_or_404   
from django.contrib import messages
from .models import Reserva, Calificacion, Reserva
from .forms import ReservaForm, ReservaEditarForm, CalificacionForm, CalificacionEditarForm
from servicios.models import Servicios

from datetime import datetime
# Create your views here.
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


def crear_reserva_user(request, servicio_id):
    # Obtenemos el servicio específico o lanzamos un error 404 si no existe
    servicio = get_object_or_404(Servicios, id=servicio_id)
    
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        
        if form.is_valid():
            reserva = form.save(commit=False)
            
            # 1. Asignamos el servicio que viene de la URL
            reserva.servicio = servicio
            
            # 2. Capturamos la fecha combinada del input oculto que llena el JS
            fecha_str = request.POST.get('fecha_reserva') # Formato: "YYYY-MM-DD HH:MM"
            try:
                reserva.fecha_reserva = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
                reserva.save()
                messages.success(request, f'¡Cita para {servicio.nombre} agendada con éxito!')
                return redirect('inicio') # Redirige a donde prefieras
            except (ValueError, TypeError):
                messages.error(request, 'Error en el formato de fecha y hora.')
        else:
            messages.error(request, 'Por favor, revisa los datos del formulario.')
    else:
        form = ReservaForm()

    context = {
        'servicio': servicio,
        'form': form,
        'titulo': f'Agendar {servicio.nombre}'
    }
    
    return render(request, 'reservas/reservas.html', context)
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
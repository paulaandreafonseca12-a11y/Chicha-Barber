from django.shortcuts import render
from django .shortcuts import render, redirect, get_object_or_404   
from django.contrib import messages
from .models import Reserva, Calificacion
from .forms import ReservaForm, ReservaEditarForm, CalificacionForm, CalificacionEditarForm
from servicios.models import Servicios
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


from django.contrib import messages
from .models import Servicios, Reserva
from .forms import ReservaForm
from datetime import datetime

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
                return redirect('perfil_usuario') # Redirige a donde prefieras
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
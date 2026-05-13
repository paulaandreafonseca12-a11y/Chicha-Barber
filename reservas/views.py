from datetime import datetime, date, timedelta

from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import Calificacion, Reserva
from .forms import CalificacionEditarForm, ReservaEditarForm
from servicios.models import Servicios
from usuarios.models import Usuario
from core.utils import enviar_correo_reserva


def _parse_fecha_reserva(fecha_str):
    if not fecha_str:
        return None
    try:
        return datetime.fromisoformat(fecha_str)
    except ValueError:
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M", "%d/%m/%Y %H:%M"):
            try:
                return datetime.strptime(fecha_str, fmt)
            except ValueError:
                continue
    return None


def obtener_disponibilidad_json(request):
    hoy = date.today()
    resultado = {}

    for i in range(3):
        fecha_evaluar = hoy + timedelta(days=i)
        reservas = Reserva.objects.filter(
            fecha_reserva__date=fecha_evaluar
        ).exclude(estado='cancelada')

        resultado[fecha_evaluar.strftime('%Y-%m-%d')] = [
            reserva.fecha_reserva.strftime('%H:%M')
            for reserva in reservas
        ]

    return JsonResponse(resultado)


def crear_reserva(request, servicio_id=None):
    if servicio_id is None:
        messages.warning(request, 'Debe seleccionar un servicio.')
        return redirect('inicio')

    servicio = get_object_or_404(Servicios, id=servicio_id)

    if request.method == 'POST':
        nombre = request.POST.get('nombre_cliente', '').strip()
        correo = request.POST.get('correo_cliente', '').strip()
        telefono = request.POST.get('telefono_cliente', '').strip()
        fecha_reserva_raw = request.POST.get('fecha_reserva', '').strip()

        if not (nombre and correo and telefono and fecha_reserva_raw):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'reservas/reservas.html', {'servicio': servicio})

        fecha_reserva = _parse_fecha_reserva(fecha_reserva_raw)
        if fecha_reserva is None:
            messages.error(request, 'Formato de fecha inválido.')
            return render(request, 'reservas/reservas.html', {'servicio': servicio})

        try:
            Reserva.objects.create(
                nombre_cliente=nombre,
                correo_cliente=correo,
                telefono_cliente=telefono,
                fecha_reserva=fecha_reserva,
                servicio=servicio,
            )
            enviar_correo_reserva(
                correo_cliente=correo,
                nombre=nombre,
                servicio=servicio,
                fecha=fecha_reserva,
            )
            messages.success(request, '¡Reserva creada con éxito!')
            return redirect('inicio')
        except Exception as e:
            messages.error(request, f'Error al crear la reserva: {e}')

    return render(request, 'reservas/reservas.html', {'servicio': servicio})


def cancelar_cita(request, pk):
    cita = get_object_or_404(Reserva, pk=pk)
    cita.estado = 'cancelada'
    cita.save()
    messages.warning(request, f'Cita cancelada: {cita.nombre_cliente}')
    return redirect('reservas:ver_agenda')


def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    form = ReservaEditarForm(request.POST or None, instance=reserva)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Reserva actualizada.')
        return redirect('reservas:ver_agenda')
    return render(request, 'reservas/editar_reserva.html', {'form': form, 'reserva': reserva})


def ver_agenda(request):
    reservas = Reserva.objects.all().order_by('-fecha_reserva')
    servicios = Servicios.objects.all()
    return render(request, 'reservas/ver_agenda.html', {
        'reservas': reservas,
        'servicios': servicios,
        'titulo': 'Agenda de Citas',
    })


def cambiar_estado_reserva(request, pk, nuevo_estado):
    reserva = get_object_or_404(Reserva, pk=pk)
    if nuevo_estado in ['reservada', 'confirmada', 'cancelada']:
        reserva.estado = nuevo_estado
        reserva.save()
        messages.info(request, f'Estado actualizado a {nuevo_estado}.')
    else:
        messages.error(request, 'Estado inválido.')
    return redirect('reservas:ver_agenda')


def reprogramar_cita(request, pk):
    cita = get_object_or_404(Reserva, pk=pk)
    form = ReservaEditarForm(request.POST or None, instance=cita)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cita reprogramada.')
        return redirect('reservas:ver_agenda')
    return render(request, 'reservas/reprogramar.html', {'form': form, 'cita': cita})


def crear_reserva_admin(request):
    servicios = Servicios.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre_cliente', '').strip()
        correo = request.POST.get('correo_cliente', '').strip()
        telefono = request.POST.get('telefono_cliente', '').strip()
        fecha_reserva_raw = request.POST.get('fecha_reserva', '').strip()
        servicio_id = request.POST.get('servicio')

        if not (nombre and correo and telefono and fecha_reserva_raw and servicio_id):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'reservas/crear_cita_admin.html', {'servicios': servicios})

        fecha_reserva = _parse_fecha_reserva(fecha_reserva_raw)
        if fecha_reserva is None:
            messages.error(request, 'Fecha de cita inválida.')
            return render(request, 'reservas/crear_cita_admin.html', {'servicios': servicios})

        try:
            servicio = Servicios.objects.get(id=servicio_id)
            Reserva.objects.create(
                nombre_cliente=nombre,
                correo_cliente=correo,
                telefono_cliente=telefono,
                fecha_reserva=fecha_reserva,
                servicio=servicio,
            )
            messages.success(request, '¡Cita registrada!')
            return redirect('reservas:ver_agenda')
        except Servicios.DoesNotExist:
            messages.error(request, 'Servicio seleccionado no existe.')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    return render(request, 'reservas/crear_cita_admin.html', {'servicios': servicios})


def calificacion_view(request):
    if request.method == 'POST':
        puntuacion = request.POST.get('puntuacion') or request.POST.get('rating')
        resena = request.POST.get('resena') or request.POST.get('comments') or ''
        if not puntuacion:
            messages.error(request, 'Por favor, selecciona una puntuación.')
            return render(request, 'calificacion/calificacion.html')

        barbero = Usuario.objects.filter(rol='barbero').first()
        if barbero is None:
            messages.error(request, 'No hay barbero asignado para la calificación.')
            return render(request, 'calificacion/calificacion.html')

        try:
            Calificacion.objects.create(
                barbero_a_calificar=barbero,
                nombre_cliente=request.user.get_full_name() if request.user.is_authenticated else 'Anónimo',
                calificacion=int(puntuacion),
                resenia=resena,
            )
            messages.success(request, '¡Gracias por tu reseña!')
            return redirect('inicio')
        except Exception as e:
            messages.error(request, f'Hubo un error al guardar tu calificación: {e}')

    return render(request, 'calificacion/calificacion.html')


def listado_calificaciones_admin(request):
    calificaciones = Calificacion.objects.all().order_by('-fecha_creacion')
    return render(request, 'reservas/listado_calificaciones_admin.html', {
        'calificaciones': calificaciones,
    })


def editar_calificacion(request, pk):
    calificacion = get_object_or_404(Calificacion, pk=pk)
    form = CalificacionEditarForm(request.POST or None, instance=calificacion)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Calificación actualizada correctamente.')
        return redirect('reservas:listado_calificaciones_admin')
    return render(request, 'reservas/editar_calificacion.html', {'form': form, 'calificacion': calificacion})

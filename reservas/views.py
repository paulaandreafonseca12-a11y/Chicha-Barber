from datetime import datetime, date, time, timedelta
from decimal import Decimal

from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

import reservas.models
from reservas.forms import ReservaEditarForm
from servicios.models import Promocion, Servicios
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


def obtener_turnos_disponibles_json(request):
    hoy = date.today()
    fin = hoy + timedelta(days=6)
    barbero_id = request.GET.get('barbero_id', 'any')

    turnos = reservas.models.Turno.objects.filter(
        fecha__range=(hoy, fin),
        estado='disponible'
    ).order_by('fecha', 'hora_inicio')

    if barbero_id and barbero_id != 'any':
        turnos = turnos.filter(profesional_id=barbero_id)

    resultado = [
        {
            'id': turno.id,
            'barbero_id': turno.profesional.id,
            'barbero': turno.profesional.get_full_name(),
            'fecha': turno.fecha.isoformat(),
            'hora': turno.hora_inicio.strftime('%H:%M'),
            'imagen': turno.profesional.foto_perfil.url if turno.profesional.foto_perfil else None,
        }
        for turno in turnos
    ]

    return JsonResponse({'turnos': resultado})


def crear_reserva(request, servicio_id=None, promocion_id=None):
    servicio = None
    promo = None

    if not request.user.is_authenticated:
        # Redirigimos al registro usando el nombre de la URL y capturando la ruta actual completa
        login_url = reverse('registro')
        return redirect(f'{login_url}?next={request.get_full_path()}')

    if promocion_id is not None:
        promo = get_object_or_404(Promocion, pk=promocion_id)
        servicio = promo.servicio
    elif servicio_id is not None:
        servicio = get_object_or_404(Servicios, id=servicio_id)
    else:
        messages.warning(request, 'Debe seleccionar un servicio o promoción.')
        return redirect('inicio')

    barberos = Usuario.objects.filter(rol='barbero', estado=True)
    
    ahora = datetime.now()
    hoy = ahora.date()
    fin = hoy + timedelta(days=6)
    
    # Obtenemos los turnos disponibles en el rango de 7 días
    turnos_qs = reservas.models.Turno.objects.filter(
        fecha__range=(hoy, fin),
        estado='disponible'
    ).order_by('fecha', 'hora_inicio')

    # FILTRO CLAVE: Solo mostrar turnos que no hayan pasado (si son de hoy)
    turnos_disponibles = [
        t for t in turnos_qs 
        if t.fecha > hoy or (t.fecha == hoy and t.hora_inicio > ahora.time())
    ]

    action_url = (
        reverse('crear_reserva_promocion', args=[promo.id])
        if promo else
        reverse('crear_reserva', args=[servicio.id])
    )

    if request.method == 'POST':
        turno_id = request.POST.get('turno_id')
        nombre = request.POST.get('nombre_cliente', '').strip()
        correo = request.POST.get('correo_cliente', '').strip()
        telefono = request.POST.get('telefono_cliente', '').strip()

        if request.user.is_authenticated and not nombre:
            nombre = request.user.get_full_name()

        # Guardamos el contexto para re-enviarlo si hay errores de validación
        context_error = {
            'servicio': servicio,
            'promo': promo,
            'barberos': barberos,
            'turnos_disponibles': turnos_disponibles,
            'action_url': action_url,
        }

        if not turno_id:
            messages.error(request, 'Selecciona un turno disponible.')
            return render(request, 'reservas/reservas.html', context_error)

        if not (nombre and correo and telefono):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'reservas/reservas.html', context_error)

        try:
            turno = reservas.models.Turno.objects.get(pk=turno_id, estado='disponible')
            precio = servicio.precio
            if promo:
                descuento = Decimal(promo.porcentaje_descuento) / Decimal('100')
                precio = round(precio * (Decimal('1') - descuento), 2)

            reservas.models.Reserva.objects.create(
                turno=turno,
                cliente=request.user if request.user.is_authenticated else None,
                nombre_cliente=nombre,
                correo_cliente=correo,
                telefono_cliente=telefono,
                servicio=servicio,
                precio_historico=precio,
            )
            turno.estado = 'reservado'
            turno.save()

            enviar_correo_reserva(
                correo_cliente=correo,
                nombre=nombre,
                servicio=servicio,
                fecha=datetime.combine(turno.fecha, turno.hora_inicio),
            )
            messages.success(request, '¡Reserva creada con éxito!')
            return redirect('inicio')
        except reservas.models.Turno.DoesNotExist:
            messages.error(request, 'El turno seleccionado ya no está disponible. Por favor elige otro.')
        except Exception as e:
            messages.error(request, f'Error al crear la reserva: {e}')

    return render(request, 'reservas/reservas.html', {
        'servicio': servicio,
        'promo': promo,
        'barberos': barberos,
        'turnos_disponibles': turnos_disponibles,
        'action_url': action_url,
    })


def cancelar_cita(request, pk):
    cita = get_object_or_404(reservas.models.Reserva, pk=pk)
    cita.estado = 'cancelada'
    cita.save()
    messages.warning(request, f'Cita cancelada: {cita.nombre_cliente}')
    return redirect('ver_agenda')


def editar_reserva(request, pk):
    reserva = get_object_or_404(reservas.models.Reserva, pk=pk)
    form = ReservaEditarForm(request.POST or None, instance=reserva)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Reserva actualizada.')
        return redirect('ver_agenda')
    return render(request, 'reservas/editar_reserva.html', {'form': form, 'reserva': reserva})


def ver_agenda(request):
    # Obtenemos las reservas y los turnos disponibles para tener una visión completa del negocio
    # Usamos select_related para traer el profesional (barbero) y el servicio en una sola consulta
    reservas = reservas.models.Reserva.objects.select_related('turno__profesional', 'servicio', 'cliente').all().order_by('-fecha_reserva')
    turnos_disponibles = reservas.models.Turno.objects.select_related('profesional').filter(
        estado='disponible'
    ).order_by('fecha', 'hora_inicio')
    servicios = Servicios.objects.all()
    return render(request, 'reservas/ver_agenda.html', {
        'reservas': reservas,
        'turnos_disponibles': turnos_disponibles,
        'servicios': servicios,
        'titulo': 'Agenda de Citas',
    })


def cambiar_estado_reserva(request, pk, nuevo_estado):
    reserva = get_object_or_404(reservas.models.Reserva, pk=pk)
    if nuevo_estado in ['reservada', 'confirmada', 'cancelada']:
        reserva.estado = nuevo_estado
        reserva.save()
        messages.info(request, f'Estado actualizado a {nuevo_estado}.')
    else:
        messages.error(request, 'Estado inválido.')
    return redirect('ver_agenda')


def reprogramar_cita(request, pk):
    cita = get_object_or_404(reservas.models.Reserva, pk=pk)
    form = ReservaEditarForm(request.POST or None, instance=cita)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cita reprogramada.')
        return redirect('ver_agenda')
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
            reservas.models.Reserva.objects.create(
                nombre_cliente=nombre,
                correo_cliente=correo,
                telefono_cliente=telefono,
                fecha_reserva=fecha_reserva,
                servicio=servicio,
            )
            messages.success(request, '¡Cita registrada!')
            return redirect('ver_agenda')
        except Servicios.DoesNotExist:
            messages.error(request, 'Servicio seleccionado no existe.')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    return render(request, 'reservas/crear_cita_admin.html', {'servicios': servicios})



def gestionar_disponibilidad_dias(request):
    """Muestra una lista de los próximos 14 días y si tienen turnos activos."""
    hoy = date.today()
    dias = []
    
    for i in range(15):
        fecha = hoy + timedelta(days=i)
        # Contamos cuántos turnos disponibles hay para ese día
        turnos_count = reservas.models.Turno.objects.filter(fecha=fecha, estado='disponible').count()
        # Contamos si hay reservas ya hechas (para no desactivar días con compromisos)
        reservas_count = reservas.models.Turno.objects.filter(fecha=fecha, estado='reservado').count()
        
        dias.append({
            'fecha': fecha,
            'disponible': turnos_count > 0,
            'cantidad': turnos_count,
            'reservas': reservas_count,
            'es_hoy': fecha == hoy
        })

    barberos = Usuario.objects.filter(rol='barbero', estado=True)

    return render(request, 'reservas/gestion_turno.html', {
        'dias': dias,
        'barberos': barberos,
        'titulo': 'Gestión de Agenda por Días'
    })


def activar_dia_agenda(request, fecha_str):
    """Crea turnos personalizados para barberos seleccionados."""
    if request.method == 'POST':
        fecha = date.fromisoformat(fecha_str)
        barbero_id = request.POST.get('barbero')
        h_inicio_val = int(request.POST.get('hora_inicio', 8))
        h_fin_val = int(request.POST.get('hora_fin', 18))
        duracion = int(request.POST.get('duracion', 60))
        # Parámetros para la hora de almuerzo
        h_almuerzo_inicio = request.POST.get('h_almuerzo_inicio')
        h_almuerzo_fin = request.POST.get('h_almuerzo_fin')

        if barbero_id == 'todos':
            barberos = Usuario.objects.filter(rol='barbero', estado=True)
        else:
            barberos = Usuario.objects.filter(id=barbero_id, rol='barbero', estado=True)

        if not barberos.exists():
            messages.error(request, "No se encontraron barberos seleccionados o activos.")
            return redirect('gestionar_dias')

        turnos_creados = 0
        for barbero in barberos:
            # Empezamos a la hora de inicio y vamos creando bloques hasta la hora de fin
            inicio_dt = datetime.combine(fecha, time(hour=h_inicio_val))
            fin_dt = datetime.combine(fecha, time(hour=h_fin_val))
            
            current = inicio_dt
            while current + timedelta(minutes=duracion) <= fin_dt:
                # Lógica para saltar la hora de almuerzo
                es_almuerzo = False
                if h_almuerzo_inicio != '' and h_almuerzo_fin != '' and h_almuerzo_inicio is not None:
                    try:
                        l_start = time(hour=int(h_almuerzo_inicio))
                        l_end = time(hour=int(h_almuerzo_fin))
                        if current.time() >= l_start and current.time() < l_end:
                            es_almuerzo = True
                    except ValueError:
                        pass
                
                if es_almuerzo:
                    current += timedelta(minutes=duracion)
                    continue

                # Evitar duplicados exactos si ya existen algunos turnos
                if not reservas.models.Turno.objects.filter(profesional=barbero, fecha=fecha, hora_inicio=current.time()).exists():
                    reservas.models.Turno.objects.create(
                        profesional=barbero,
                        fecha=fecha,
                        hora_inicio=current.time(),
                        hora_fin=(current + timedelta(minutes=duracion)).time(),
                        estado='disponible'
                    )
                    turnos_creados += 1
                current += timedelta(minutes=duracion)

        messages.success(request, f"Día {fecha_str} configurado. Se crearon {turnos_creados} turnos.")
    return redirect('gestionar_dias')



def desactivar_dia_agenda(request, fecha_str):
    """Elimina solo los turnos que están 'disponibles' para una fecha, ocultándola del cliente."""
    fecha = date.fromisoformat(fecha_str)
    eliminados, _ = reservas.models.Turno.objects.filter(fecha=fecha, estado='disponible').delete()
    messages.warning(request, f"Día {fecha_str} desactivado. Se eliminaron {eliminados} turnos disponibles.")
    return redirect('gestionar_dias')

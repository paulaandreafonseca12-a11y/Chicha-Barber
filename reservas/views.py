from datetime import datetime, date, time, timedelta
from decimal import Decimal
from django.db import transaction
from django.urls import reverse
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from reservas.models import Reserva, Agenda
from reservas.forms import ReservaEditarForm
from servicios.models import Promocion, Servicios
from usuarios.models import Usuario, Notificacion  # <-- Importamos Notificacion
from core.utils import enviar_correo_reserva, enviar_correo_cancelacion_admin


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

    agendas = Agenda.objects.filter(
        fecha__range=(hoy, fin),
        estado='disponible'
    ).order_by('fecha', 'hora_inicio')

    if barbero_id and barbero_id != 'any':
        agendas = agendas.filter(profesional_id=barbero_id)

    resultado = [
        {
            'id': agenda.id,
            'barbero_id': agenda.profesional.id,
            'barbero': agenda.profesional.get_full_name(),
            'fecha': agenda.fecha.isoformat(),
            'hora': agenda.hora_inicio.strftime('%H:%M'),
            'imagen': agenda.profesional.foto_perfil.url if agenda.profesional.foto_perfil else None,
        }
        for agenda in agendas
    ]

    return JsonResponse({'turnos': resultado})


def crear_reserva(request, servicio_id=None, promocion_id=None):
    servicio = None
    factura_id = request.GET.get('factura_id') or request.POST.get('factura_id')
    promo = None

    if not request.user.is_authenticated:
        login_url = reverse('login')
        return redirect(f'{login_url}?next={request.get_full_path()}')

    if promocion_id is not None:
        promo = get_object_or_404(Promocion, pk=promocion_id)
        servicio = promo.servicio
    elif servicio_id is not None:
        servicio = get_object_or_404(Servicios, id=servicio_id)
    else:
        messages.warning(request, 'Debe seleccionar un servicio o promoción.')
        return redirect('inicio')

    if request.user.is_authenticated and 'reserva_pendiente' in request.session:
        reserva_data = request.session.pop('reserva_pendiente')
        turno_id = reserva_data.get('turno_id')
        nombre = reserva_data.get('nombre_cliente') or request.user.get_full_name()
        correo = reserva_data.get('correo_cliente') or request.user.email
        telefono = reserva_data.get('telefono_cliente')

        try:
            agenda_obj = Agenda.objects.get(pk=turno_id, estado='disponible')
            precio = servicio.precio
            if promo:
                descuento = Decimal(promo.porcentaje_descuento) / Decimal('100')
                precio = round(precio * (Decimal('1') - descuento), 2)

            reserva = Reserva.objects.create(
                agenda=agenda_obj,  # <-- Actualizado de 'turno' a 'agenda'
                cliente=request.user,
                nombre_cliente=nombre,
                correo_cliente=correo,
                telefono_cliente=telefono,
                servicio=servicio,
                precio_historico=precio,
            )
            agenda_obj.estado = 'reservada'
            agenda_obj.save()

            factura = Factura.objects.create(
                cliente=request.user,
                total_pagado=0,
                metodo_pago='efectivo',
                estado='pendiente'
            )
            DetalleFactura.objects.create(
                factura=factura,
                reserva=reserva,
                cantidad=1,
                precio_unitario=precio,
                subtotal=precio
            )

            enviar_correo_reserva(
                correo_cliente=correo,
                nombre=nombre,
                servicio=servicio,
                fecha=datetime.combine(agenda_obj.fecha, agenda_obj.hora_inicio),
            )
            messages.success(request, '¡Te has registrado con éxito y tu reserva ha sido confirmada!')
            return redirect(f"{reverse('carrito')}?reserva_id={reserva.id}&reserva_servicio={reserva.servicio.nombre}&reserva_fecha={agenda_obj.fecha.isoformat()}&reserva_hora={agenda_obj.hora_inicio.strftime('%H:%M')}&reserva_precio={float(reserva.precio_historico or precio)}&factura_id={factura.id}")
        except Agenda.DoesNotExist:
            messages.error(request, 'El turno que habías seleccionado ya no está disponible.')
        except Exception as e:
            messages.error(request, f'Error al procesar tu reserva pendiente: {e}')

    barberos = Usuario.objects.filter(rol='barbero', estado=True)
    ahora = datetime.now()
    hoy = ahora.date()
    fin = hoy + timedelta(days=6)
    
    turnos_qs = Agenda.objects.filter(
        fecha__range=(hoy, fin),
        estado='disponible'
    ).order_by('fecha', 'hora_inicio')

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

        if not request.user.is_authenticated:
            request.session['reserva_pendiente'] = {
                'turno_id': turno_id,
                'nombre_cliente': nombre,
                'correo_cliente': correo,
                'telefono_cliente': telefono,
            }
            messages.info(request, 'Por favor, regístrate o inicia sesión para confirmar tu reserva.')
            login_url = reverse('registro')
            return redirect(f'{login_url}?next={request.get_full_path()}')

        if not nombre:
            nombre = request.user.get_full_name()

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
            with transaction.atomic():
                agenda_obj = Agenda.objects.select_for_update().get(pk=turno_id, estado='disponible')
                
                precio = servicio.precio
                if promo:
                    descuento = Decimal(promo.porcentaje_descuento) / Decimal('100')
                    precio = round(precio * (Decimal('1') - descuento), 2)

                reserva = Reserva.objects.create(
                    agenda=agenda_obj,
                    cliente=request.user if request.user.is_authenticated else None,
                    nombre_cliente=nombre,
                    correo_cliente=correo,
                    telefono_cliente=telefono,
                    servicio=servicio,
                    precio_historico=precio,
                    promocion=promo,
                )
                agenda_obj.estado = 'reservada'
                agenda_obj.save()

                if factura_id:
                    factura = get_object_or_404(Factura, id=factura_id)
                else:
                    factura = Factura.objects.create(
                        cliente=request.user,
                        total_pagado=0,
                        metodo_pago='efectivo',
                        estado='pendiente'
                    )

                DetalleFactura.objects.create(
                    factura=factura,
                    reserva=reserva,
                    cantidad=1,
                    precio_unitario=precio,
                    subtotal=precio
                )

            try:
                enviar_correo_reserva(
                    correo_cliente=correo,
                    nombre=nombre,
                    servicio=servicio,
                    fecha=datetime.combine(agenda_obj.fecha, agenda_obj.hora_inicio),
                )
            except Exception as mail_error:
                print(f"Error al enviar correo de reserva: {mail_error}")

            return redirect(f"{reverse('carrito')}?reserva_id={reserva.id}&reserva_servicio={reserva.servicio.nombre}&reserva_fecha={agenda_obj.fecha.isoformat()}&reserva_hora={agenda_obj.hora_inicio.strftime('%H:%M')}&reserva_precio={float(reserva.precio_historico or precio)}&factura_id={factura.id}")
        except Agenda.DoesNotExist:
            reserva_existente = Reserva.objects.filter(agenda_id=turno_id).first()
            if reserva_existente:
                return redirect(f"{reverse('carrito')}?reserva_id={reserva_existente.id}&reserva_servicio={reserva_existente.servicio.nombre}&reserva_fecha={reserva_existente.agenda.fecha.isoformat()}&reserva_hora={reserva_existente.agenda.hora_inicio.strftime('%H:%M')}&reserva_precio={float(reserva_existente.precio_historico or 0)}")
            messages.error(request, '¡Ups! El turno seleccionado ya no está disponible. Por favor elige otro.')
        except Exception as e:
            messages.error(request, f'Error al crear la reserva: {e}')

    context = {
        'servicio': servicio,
        'promo': promo,
        'barberos': barberos,
        'turnos_disponibles': turnos_disponibles,
        'action_url': action_url,
    }

    return render(request, 'reservas/reservas.html', context)


def reserva_confirmada(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    context = {'reserva': reserva}
    return render(request, 'reservas/reserva_confirmada.html', context)


@login_required
def cancelar_cita(request, pk):
    cita = get_object_or_404(Reserva, pk=pk)
    cita.estado = 'cancelada'
    cita.save()
    
    Notificacion.objects.create(
        usuario=request.user,
        mensaje=f'Se canceló tu cita del {cita.agenda.fecha}' # <-- Actualizado a agenda.fecha
    )
    admins = Usuario.objects.filter(rol='admin')
    for admin in admins:
        Notificacion.objects.create(
            usuario=admin,
            mensaje=f'{request.user.get_full_name()} canceló una cita.'
        )
    messages.warning(request, f'Cita cancelada: {cita.nombre_cliente}')
    return redirect('ver_agenda')


@login_required
def editar_reserva(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    form = ReservaEditarForm(request.POST or None, instance=reserva)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Reserva actualizada.')
        return redirect('ver_agenda')

    context = {
        'form': form,
        'reserva': reserva,
    }
    return render(request, 'reservas/editar_reserva.html', context)


@login_required
def ver_agenda(request):
    if request.user.rol not in ['admin', 'barbero']:
        messages.error(request, "No tienes permiso para ver la agenda.")
        return redirect('inicio')

    hoy_fecha = date.today()
    mes_actual = hoy_fecha.month
    anio_actual = hoy_fecha.year

    total_citas_mes = Reserva.objects.filter(
        agenda__fecha__month=mes_actual, # <-- Actualizado a agenda
        agenda__fecha__year=anio_actual
    ).exclude(estado='cancelada').count()

    turnos_disponibles_hoy = Agenda.objects.filter(
        fecha=hoy_fecha,
        estado='disponible'
    ).count()

    citas_canceladas_mes = Reserva.objects.filter(
        agenda__fecha__month=mes_actual,
        agenda__fecha__year=anio_actual,
        estado='cancelada'
    ).count()

    lista_reservas = Reserva.objects.select_related('agenda__profesional', 'servicio', 'cliente').all().order_by('-agenda__fecha', '-agenda__hora_inicio')
    turnos_disponibles = Agenda.objects.select_related('profesional').filter(
        estado='disponible'
    ).order_by('fecha', 'hora_inicio')
    servicios = Servicios.objects.all()

    context = {
        'reservas': lista_reservas,
        'turnos_disponibles': turnos_disponibles,
        'servicios': servicios,
        'titulo': 'Agenda de Citas',
        'total_citas_mes': total_citas_mes,
        'turnos_disponibles_hoy': turnos_disponibles_hoy,
        'citas_canceladas_mes': citas_canceladas_mes,
    }
    return render(request, 'reservas/ver_agenda.html', context)


@login_required
def cambiar_estado_reserva(request, pk, nuevo_estado):
    reserva = get_object_or_404(Reserva, pk=pk)
    if nuevo_estado in ['reservada', 'confirmada', 'cancelada']:
        reserva.estado = nuevo_estado
        reserva.save()
        messages.info(request, f'Estado actualizado a {nuevo_estado}.')
    else:
        messages.error(request, 'Estado inválido.')
    return redirect('ver_agenda')


@login_required
def reprogramar_cita(request, pk):
    cita = get_object_or_404(Reserva, pk=pk)
    form = ReservaEditarForm(request.POST or None, instance=cita)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Cita reprogramada.')
        return redirect('ver_agenda')

    context = {
        'form': form,
        'cita': cita,
    }
    return render(request, 'reservas/reprogramar.html', context)


@login_required
def crear_reserva_admin(request):
    if not (request.user.is_staff or request.user.rol == 'admin'):
        messages.error(request, "Acceso restringido a administradores.")
        return redirect('ver_agenda')

    servicios = Servicios.objects.all()

    if request.method == 'POST':
        nombre = request.POST.get('nombre_cliente', '').strip()
        correo = request.POST.get('correo_cliente', '').strip()
        telefono = request.POST.get('telefono_cliente', '').strip()
        fecha_reserva_raw = request.POST.get('fecha_reserva', '').strip()
        servicio_id = request.POST.get('servicio')
        barbero_id = request.POST.get('barbero') 

        if not (nombre and correo and telefono and fecha_reserva_raw and servicio_id):
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'reservas/crear_cita_admin.html', {'servicios': servicios})
        
        fecha_reserva = _parse_fecha_reserva(fecha_reserva_raw)
        if fecha_reserva is None:
            messages.error(request, 'Fecha de cita inválida.')
            return render(request, 'reservas/crear_cita_admin.html', {'servicios': servicios})
    
        try:
            with transaction.atomic():
                servicio = Servicios.objects.get(id=servicio_id)
                
                # <-- Actualizado de Turno.objects a Agenda.objects
                turno_coincidente = Agenda.objects.filter(
                    fecha=fecha_reserva.date(),
                    hora_inicio=fecha_reserva.time(),
                    profesional_id=barbero_id,
                    estado='disponible'
                ).first()

                Reserva.objects.create(
                    agenda=turno_coincidente, # <-- Actualizado
                    nombre_cliente=nombre,
                    correo_cliente=correo,
                    telefono_cliente=telefono,
                    fecha_reserva=fecha_reserva,
                    servicio=servicio,
                )
                if turno_coincidente:
                    turno_coincidente.estado = 'reservada'
                    turno_coincidente.save()

            messages.success(request, '¡Cita registrada!')
            return redirect('ver_agenda')
        except Servicios.DoesNotExist:
            messages.error(request, 'Servicio seleccionado no existe.')
        except Exception as e:
            messages.error(request, f'Error: {e}')

    context = {'servicios': servicios}
    return render(request, 'reservas/crear_cita_admin.html', context)


@login_required
def gestionar_disponibilidad_dias(request):
    if not (request.user.is_staff or request.user.rol == 'admin'):
        messages.error(request, "No tienes permisos para gestionar la disponibilidad.")
        return redirect('ver_agenda')

    hoy = date.today()
    dias = []
    
    for i in range(15):
        fecha = hoy + timedelta(days=i)
        turnos_count = Agenda.objects.filter(fecha=fecha, estado='disponible').count()
        reservas_count = Agenda.objects.filter(fecha=fecha, estado='reservada').count() # <-- Actualizado a 'reservada'
        
        dias.append({
            'fecha': fecha,
            'disponible': turnos_count > 0,
            'cantidad': turnos_count,
            'reservas': reservas_count,
            'es_hoy': fecha == hoy
        })

    barberos = Usuario.objects.filter(rol='barbero', estado=True)

    context = {
        'dias': dias,
        'barberos': barberos,
        'titulo': 'Gestión de Agenda por Días'
    }
    return render(request, 'reservas/gestion_turno.html', context)


@login_required
def activar_dia_agenda(request, fecha_str):
    if not (request.user.is_staff or request.user.rol == 'admin'):
        messages.error(request, "Acceso denegado.")
        return redirect('ver_agenda')

    if request.method == 'POST':
        fecha = date.fromisoformat(fecha_str)
        barbero_id = request.POST.get('barbero')
        h_inicio_val = int(request.POST.get('hora_inicio', 8))
        h_fin_val = int(request.POST.get('hora_fin', 18))
        duracion = int(request.POST.get('duracion', 60))
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
            inicio_dt = datetime.combine(fecha, time(hour=h_inicio_val))
            fin_dt = datetime.combine(fecha, time(hour=h_fin_val))
            
            current = inicio_dt
            while current + timedelta(minutes=duracion) <= fin_dt:
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

                if not Agenda.objects.filter(profesional=barbero, fecha=fecha, hora_inicio=current.time()).exists():
                    Agenda.objects.create(
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


@login_required
def desactivar_dia_agenda(request, fecha_str):
    if not (request.user.is_staff or request.user.rol == 'admin'):
        messages.error(request, "Acceso denegado.")
        return redirect('ver_agenda')

    fecha = date.fromisoformat(fecha_str)
    
    reservas_afectadas = Reserva.objects.filter(
        agenda__fecha=fecha, # <-- Actualizado a agenda
        estado__in=['reservada', 'confirmada']
    )
    
    cantidad_notificada = 0
    for reserva in reservas_afectadas:
        reserva.estado = 'cancelada'
        reserva.save()
        
        try:
            enviar_correo_cancelacion_admin(
                correo_cliente=reserva.correo_cliente,
                nombre=reserva.nombre_cliente,
                servicio=reserva.servicio.nombre,
                fecha=reserva.fecha_reserva
            )
            cantidad_notificada += 1
        except Exception as e:
            print(f"Error al notificar a {reserva.correo_cliente}: {e}")

    Agenda.objects.filter(fecha=fecha, estado='disponible').delete()
    
    if cantidad_notificada > 0:
        messages.success(request, f"Se cancelaron {cantidad_notificada} citas y se enviaron los correos de notificación.")
    
    messages.warning(request, f"Día {fecha_str} desactivado. No se aceptarán más reservas para esta fecha.")
    
    return redirect('gestionar_dias')
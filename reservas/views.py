from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from datetime import datetime
from .models import Reserva, Calificacion
from datetime import datetime, date, timedelta

from django.http import JsonResponse

from .models import Calificacion, Reserva
from .forms import (
    ReservaForm,
    ReservaEditarForm,
    CalificacionForm,
    CalificacionEditarForm,
)
from servicios.models import Servicios 

from servicios.models import Servicios

# 📧 IMPORTANTE: correo reserva
from core.utils import enviar_correo_reserva


# =========================
# 📅 DISPONIBILIDAD JSON
# =========================

def obtener_disponibilidad_json(request):

    hoy = date.today()
    resultado = {}

    for i in range(3):

        fecha_evaluar = hoy + timedelta(days=i)

        reservas = Reserva.objects.filter(
            fecha_reserva__date=fecha_evaluar
        ).exclude(
            estado='cancelada'
        )

        fecha_key = fecha_evaluar.strftime('%Y-%m-%d')

        horas = []

        for reserva in reservas:
            hora = reserva.fecha_reserva.strftime('%H:%M')
            horas.append(hora)

        resultado[fecha_key] = horas

    return JsonResponse(resultado)


# =========================
# 🔹 CREAR RESERVA CLIENTE
# =========================

def crear_reserva(request, servicio_id):
    servicio = get_object_or_404(Servicios, id=servicio_id)
    form = ReservaForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.servicio = servicio
            fecha_str = request.POST.get('fecha_reserva')
            try:
                # Ajustado para que coincida con el formato de fecha que manejes
                reserva.fecha_reserva = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
                reserva.save()
                messages.success(request, f'¡Cita para {servicio.nombre} agendada!')
                return redirect('reservas:ver_agenda')
            except (ValueError, TypeError):
                messages.error(request, 'Formato de fecha inválido.')

    return render(request, 'reservas/reservas.html', {'servicio': servicio, 'form': form})

    servicio = get_object_or_404(Servicios, id=servicio_id)

    if request.method == 'POST':

        try:

            nombre = request.POST.get('nombre_cliente')
            correo = request.POST.get('correo_cliente')
            telefono = request.POST.get('telefono_cliente')
            fecha_reserva = request.POST.get('fecha_reserva')

            fecha_convertida = datetime.strptime(
                fecha_reserva,
                "%Y-%m-%d %H:%M"
            )

            # 💾 GUARDAR RESERVA
            reserva = Reserva.objects.create(
                nombre_cliente=nombre,
                correo_cliente=correo,
                telefono_cliente=telefono,
                fecha_reserva=fecha_convertida,
                servicio=servicio,
            )

            # 📧 ENVIAR CORREO
            enviar_correo_reserva(
                correo_cliente=correo,
                nombre=nombre,
                servicio=servicio,
                fecha=fecha_convertida
            )

            messages.success(request, '¡Reserva creada con éxito!')

            return redirect('inicio')

        except Exception as e:

            print(e)
            messages.error(request, f'Error al crear reserva: {e}')

    return render(
        request,
        'reservas/reservas.html',
        {
            'servicio': servicio,
            'titulo': f'Agendar {servicio.nombre}'
        }
    )


# =========================
# ❌ CANCELAR CITA
# =========================

def cancelar_cita(request, pk):

    cita = get_object_or_404(Reserva, pk=pk)

    cita.estado = 'cancelada'
    cita.save()

    messages.warning(
        request,
        f"Cita cancelada: {cita.nombre_cliente}"
    )

    return redirect('reservas:ver_agenda')


# =========================
# ✏️ EDITAR RESERVA
# =========================

def editar_reserva(request, pk):

    reserva = get_object_or_404(Reserva, pk=pk)

    form = ReservaEditarForm(request.POST or None, instance=reserva)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Reserva actualizada.')
        return redirect('reservas:ver_agenda')
    return render(request, 'reservas/editar_reserva.html', {'form': form})

    if request.method == 'POST':

        if form.is_valid():

            form.save()

            messages.success(request, 'Reserva actualizada.')
            return redirect('reservas:ver_agenda')

    return render(
        request,
        'reservas/editar_reserva.html',
        {
            'form': form,
            'titulo': 'Editar Reserva'
        }
    )


# =========================
# ⭐ CALIFICACIONES (CLIENTE)
# =========================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Calificacion
from .forms import CalificacionForm

def calificacion_view(request):
    print(f"MÉTODO RECIBIDO: {request.method}") # Ver en consola
    if request.method == 'POST':
        print(f"DATOS DEL POST: {request.POST}") # ESTO NOS DIRÁ TODO
        
        puntuacion_v = request.POST.get('puntuacion')
        resena_v = request.POST.get('resena')
        
        if not puntuacion_v:
            # Si entramos aquí, la consola nos dirá por qué
            messages.error(request, 'Por favor, selecciona una puntuación.')
            return render(request, 'calificacion/calificacion.html')
        # ... resto del código ...

        try:
            nueva_calificacion = Calificacion(
                puntuacion=int(puntuacion_v),
                resena=resena_v,
                usuario=request.user if request.user.is_authenticated else None
            )
            nueva_calificacion.save()
            messages.success(request, '¡Gracias por tu reseña!')
            return redirect('inicio')
        except Exception as e:
            print(f"Error al guardar: {e}")
            messages.error(request, 'Hubo un error al guardar tu calificación.')
    
    return render(request, 'calificacion/calificacion.html')
# =========================
# 🔧 ADMIN / GESTIÓN
# =========================

def listado_calificaciones_admin(request):
    # Esta es la vista que muestra la tabla que ya arreglamos
    calificaciones = Calificacion.objects.all().order_by('-fecha')
    return render(request, 'reservas/listado_calificaciones_admin.html', {
        'calificaciones': calificaciones
    })

    form = CalificacionForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():

            form.save()

            messages.success(request, '¡Gracias por calificar!')
            return redirect('reservas:calificacion')

    return render(
        request,
        'calificacion/calificacion.html',
        {'form': form}
    )


def editar_calificacion(request, pk):

    calificacion = get_object_or_404(Calificacion, pk=pk)
    # Asegúrate de usar el nombre correcto del formulario que definimos antes

    form = CalificacionEditarForm(request.POST or None, instance=calificacion)

    if request.method == 'POST':

        if form.is_valid():

            form.save()
            messages.success(request, 'Calificación actualizada correctamente.')
            return redirect('reservas:listado_calificaciones_admin')

    return render(request, 'reservas/editar_calificacion.html', {'form': form})
def ver_agenda(request):
    reservas = Reserva.objects.all().order_by('-fecha_creacion')
    servicios = Servicios.objects.all() 
    return render(request, 'reservas/ver_agenda.html', {
        'reservas': reservas,
        'servicios': servicios
    })


            messages.success(request, 'Calificación actualizada.')
            return redirect('reservas:calificacion')

    return render(
        request,
        'reservas/editar_calificacion.html',
        {'form': form}
    )


# =========================
# 📅 VER AGENDA
# =========================

def ver_agenda(request):

    reservas = Reserva.objects.all().order_by('-fecha_reserva')
    servicios = Servicios.objects.all()

    return render(
        request,
        'reservas/ver_agenda.html',
        {
            'reservas': reservas,
            'servicios': servicios,
            'titulo': 'Agenda de Citas'
        }
    )


# =========================
# 🔄 CAMBIAR ESTADO
# =========================

def cambiar_estado_reserva(request, pk, nuevo_estado):

    reserva = get_object_or_404(Reserva, pk=pk)

    if nuevo_estado in ['reservada', 'confirmada', 'cancelada']:

        reserva.estado = nuevo_estado
        reserva.save()

        messages.info(
            request,
            f"Estado actualizado a {nuevo_estado}"
        )

    return redirect('reservas:ver_agenda')


# =========================
# 🔁 REPROGRAMAR CITA
# =========================

def reprogramar_cita(request, pk):

    cita = get_object_or_404(Reserva, pk=pk)

    form = EditarReservaForm(request.POST or None, instance=cita)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Cita reprogramada")
        return redirect('reservas:ver_agenda')
    return render(request, 'reservas/reprogramar.html', {'form': form, 'cita': cita})

def crear_reserva_admin(request):
    if request.method == 'POST':

        if form.is_valid():

            form.save()

            messages.success(request, "Cita reprogramada")
            return redirect('reservas:ver_agenda')

    return render(
        request,
        'reservas/reprogramar.html',
        {
            'form': form,
            'cita': cita
        }
    )


# =========================
# 🛠️ CREAR RESERVA ADMIN
# =========================

def crear_reserva_admin(request):

    servicios = Servicios.objects.all()
    if request.method == 'POST':
        try:
            Reserva.objects.create(
                nombre_cliente=request.POST.get('nombre_cliente'),
                correo_cliente=request.POST.get('correo_cliente'),
                telefono_cliente=request.POST.get('telefono_cliente'),
                fecha_reserva=request.POST.get('fecha_reserva'),
                servicio=Servicios.objects.get(id=request.POST.get('servicio')),
            )
            messages.success(request, "¡Cita registrada!")
            return redirect('reservas:ver_agenda')
        except Exception as e:
            messages.error(request, f"Error: {e}")
    return render(request, 'reservas/crear_cita_admin.html', {'servicios': servicios})

        try:

            nombre = request.POST.get('nombre_cliente')
            correo = request.POST.get('correo_cliente')
            telefono = request.POST.get('telefono_cliente')
            fecha_reserva = request.POST.get('fecha_reserva')
            servicio_id = request.POST.get('servicio')

            servicio = Servicios.objects.get(id=servicio_id)

            fecha_convertida = datetime.strptime(
                fecha_reserva,
                "%Y-%m-%d %H:%M"
            )

            # 💾 GUARDAR
            reserva = Reserva.objects.create(
                nombre_cliente=nombre,
                correo_cliente=correo,
                telefono_cliente=telefono,
                fecha_reserva=fecha_convertida,
                servicio=servicio,
            )

            # 📧 ENVIAR CORREO
            enviar_correo_reserva(
                correo_cliente=correo,
                nombre=nombre,
                servicio=servicio,
                fecha=fecha_convertida
            )

            messages.success(request, '¡Cita registrada con éxito!')

            return redirect('inicio')

        except Exception as e:

            print(e)
            messages.error(request, f'Error al guardar: {e}')

    return render(
        request,
        'reservas/crear_cita_admin.html',
        {'titulo': "Crear Reserva", 'servicios': servicios}
    )

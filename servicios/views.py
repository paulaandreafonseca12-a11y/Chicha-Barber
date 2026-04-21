from django.shortcuts import render # type: ignore
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib import messages

import servicios # type: ignore
from .models import *
from .forms import PromocionEditarForm, PromocionForm, ServiciosForm, ServiciosEditarForm
from.models import Servicios, Promocion 

         

def servicios_view(request):
    servicios = Servicios.objects.all()
    
    context = {
        'titulo': 'Nuestros Servicios',
        'servicios': servicios  
    }
    return render(request, 'servicios/servicios.html', context)
def servicios_admin_view(request):
    servicios = Servicios.objects.all()
    
    context = {
        'titulo': 'Nuestros Servicios',
        'servicios': servicios
    }
    return render(request, 'servicios/listado-admin.html', context)

def calificacion_views(request):
    context = {
        'titulo': 'Calificación de Servicios',
    }
    return render(request, 'calificacion.html', context)

def crear_servicios(request):
    if request.method == 'POST':
        form = ServiciosForm(request.POST)
        if form.is_valid():
            servicio = form.save(commit=False)
            
            # 1. Asignar el documento como nombre de usuario
            servicio.username = servicio.documento
            
            
            
            # 4. Ahora sí guardamos en la base de datos
            servicio.save()
        else:
            messages.error(request, "Error al crear el servicio. Revisa los campos marcados en rojo.")
    else:
        form = ServiciosForm()
    
    context={
        'form': form,
        'titulo': 'Crear nuevo servicio',
    }
    return render(request, 'servicios/agregar_servicio.html', context)


def editar_servicios(request, pk):
    servicio = get_object_or_404(Servicios, pk=pk) #pk es igual que id, pero pk es más genérico y se usa para cualquier modelo, no solo para Servicios. Es una buena práctica usar pk en las vistas genéricas de Django.

    if request.method == 'POST':
        form = ServiciosEditarForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, f"Datos de {servicio.nombre} actualizados correctamente.")
            return redirect('listado-servicios')
        else:
            messages.error(request, "Error al actualizar. Revisa los campos marcados en rojo.")
    else:
        form = ServiciosForm(instance=servicio)

    context = {
        'form': form,
        'titulo': f'Editar a {servicio.nombre}',
    }
    return render(request, 'servicios/editar_servicios.html', context)

def eliminar_servicios(request, id):
    servicio = get_object_or_404(Servicios, id=id)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, 'Servicio eliminado del sistema.')
        return redirect('listar_fichas')
    return render(request, 'usuarios/confirmar_eliminacion.html', {'servicio': servicio})

def promocion(request):
    promociones = Promocion.objects.all()
    context = {
        'titulo': 'Promociones',
        'promociones': promociones  # ← agregado
    }
    return render(request, 'promocion.html', context)

def seleccionar_promocion(request, nombre_promo):
    
    # Guardamos la promoción en la sesión
    request.session['promocion_seleccionada'] = nombre_promo
    
    # Mandamos un mensaje de éxito opcional para la página de reservas
    messages.success(request, f"✅ Has seleccionado la promoción: {nombre_promo}")
    
    # Redirigimos a la página de reservas
    return redirect('reservas') # Asegúrate que este name sea el correcto

def crear_promocion(request):
    if request.method == 'POST':
        form = PromocionForm(request.POST)
        if form.is_valid():
            Promocion = form.save(commit=False)
            
            # 4. Ahora sí guardamos en la base de datos
            promocion.save()
            messages.success(request, "Promoción creada exitosamente.")
            return redirect('listado-promocion')
        else:
            messages.error(request, "Error al crear la promoción. Revisa los campos marcados en rojo.")
    else:
        form = PromocionForm()
    
    context={
        'form': form,
        'titulo': 'Crear nueva promoción',
    }
    return render(request, 'servicios/agregar_promocion.html', context)


def editar_promocion(request, pk):
    promocion = get_object_or_404(Promocion, pk=pk) #pk es igual que id, pero pk es más genérico y se usa para cualquier modelo, no solo para Promocion. Es una buena práctica usar pk en las vistas genéricas de Django.

    if request.method == 'POST':
        form = PromocionEditarForm(request.POST, instance=promocion)
        if form.is_valid():
            form.save()
            messages.success(request, f"Datos de {promocion.nombre} actualizados correctamente.")
            return redirect('listado-promocion')
        else:
            messages.error(request, "Error al actualizar. Revisa los campos marcados en rojo.")
    else:
        form = PromocionForm(instance=promocion)

    context = {
        'form': form,
        'titulo': f'Editar a {promocion.nombre}',
    }
    return render(request, 'servicios/editar_promocion.html', context)

    
def listado_promocion(request):
    servicios = Servicios.objects.all()
    promociones = Promocion.objects.all()
    
    context = {
        'titulo': 'Listado de Servicios y Promociones',
        'servicios': servicios,
        'promociones': promociones
    }
    return render(request, 'servicios/listado-promocion.html', context)

def eliminar_promocion(request, id):
    promocion = get_object_or_404(Promocion, id=id)
    if request.method == 'POST':
        promocion.delete()
        messages.success(request, 'Promoción eliminada del sistema.')
        return redirect('listar_promociones')
    return render(request, 'usuarios/confirmar_eliminacion.html', {'promocion': promocion})
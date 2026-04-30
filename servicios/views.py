from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from reservas.models import Calificacion
# Eliminados imports redundantes y corregido el import de modelos
from .models import Servicios, Promocion 
from .forms import PromocionEditarForm, PromocionForm, ServiciosForm, ServiciosEditarForm

def servicios(request):
    servicios = Servicios.objects.all()
    context = {
        'titulo': 'Nuestros Servicios',
        'servicios': servicios 
    }
    return render(request, 'servicios/servicios.html', context)

def servicios_admin(request):
    servicios = Servicios.objects.all()
    context = {
        'titulo': 'Administración de Servicios',
        'servicios': servicios  
    }
    return render(request, 'servicios/listado-admin.html', context)

def crear_servicios(request):
    if request.method == 'POST':
        form = ServiciosForm(request.POST, request.FILES)
        if form.is_valid():
            # Limpiamos lógica innecesaria y guardamos directamente
            form.save()
            messages.success(request, "Servicio creado con éxito.")
            return redirect('listado-admin') 
        else:
            messages.error(request, "Error al crear el servicio. Revisa los campos.")
    else:
        form = ServiciosForm()
    
    return render(request, 'servicios/agregar_servicios.html', {'form': form, 'titulo': 'Crear nuevo servicio'})
def promocion(request):
    promociones = Promocion.objects.all()
    context = {
        'titulo': 'Promociones',
        'promociones': promociones
    }
    return render(request, 'servicios/promocion.html', context)

def listado_admin(request):
    servicios = Servicios.objects.all()
    context = {
        'titulo': 'Listado de Servicios', # Título corregido para reflejar que es un listado
        'servicios': servicios
    }
    return render(request, 'servicios/listado-admin.html', context)

def listado_promocion(request):
    promociones = Promocion.objects.all()
    context = {
        'titulo': 'Listado de Promociones',
        'promociones': promociones
    }
    return render(request, 'servicios/listado-promocion.html', context)
def editar_servicios(request, pk):
    servicio = get_object_or_404(Servicios, pk=pk)
    if request.method == 'POST':
        form = ServiciosEditarForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, f"Servicio {servicio.nombre} actualizado.")
            return redirect('listado-admin')
    else:
        form = ServiciosEditarForm(instance=servicio)
    context = {
        'form': form,
        'servicio': servicio
        }

    return render(request, 'servicios/editar_servicios.html', context)

def eliminar_servicios(request, pk):
    servicio = get_object_or_404(Servicios, pk=pk)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, 'Servicio eliminado.')
        return redirect('listado-admin')
    return render(request, 'servicios/eliminar_servicios.html', {'servicio': servicio})

def crear_promocion(request):
    if request.method == 'POST':
        form = PromocionForm(request.POST, request.FILES)
        if form.is_valid():
            # ERROR CORREGIDO: No uses "Promocion = ..." porque borras la clase del Modelo
            nueva_promo = form.save() 
            messages.success(request, "Promoción creada exitosamente.")
            return redirect('listado_promocion')
        else:
            messages.error(request, "Error al crear la promoción.")
    else:
        form = PromocionForm()
    
    return render(request, 'servicios/agregar_promocion.html', {'form': form, 'titulo': 'Crear nueva promoción'})

def editar_promocion(request, pk):
    promocion = get_object_or_404(Promocion, pk=pk)
    if request.method == 'POST':
        form = PromocionEditarForm(request.POST, request.FILES, instance=promocion)
        if form.is_valid():
            form.save()
            messages.success(request, f"Promoción {promocion.nombre} actualizada.")
            return redirect('listado-promocion')
    else:
        # ERROR CORREGIDO: Aquí usabas PromocionForm en lugar de Editar si correspondía
        form = PromocionEditarForm(instance=promocion)

    return render(request, 'servicios/editar_promocion.html', {'form': form, 'promocion': promocion})

def eliminar_promocion(request, pk):
    promocion = get_object_or_404(Promocion, pk=pk)
    if request.method == 'POST':
        promocion.delete()
        messages.success(request, 'Promoción eliminada.')
        return redirect('listado_promocion') # Verifica que este name sea correcto en urls.py
    return render(request, 'servicios/eliminar_promocion.html', {'promocion': promocion})

def listado_calificacion(request):
    calificacion = Calificacion.objects.all()
    context = {
        'titulo': 'Listado de Calificaciones',
        'calificacion': calificacion
    }
    return render(request, 'servicios/listado-promocion.html', context)

def crear_promocion(request):
    if request.method == 'POST':
        form = PromocionForm(request.POST)
        if form.is_valid():
            form.save() 
            messages.success(request, "Promoción creada exitosamente.")
            return redirect('listado-promocion')
    else:
        form = PromocionForm()
    return render(request, 'servicios/agregar_promocion.html', {'form': form, 'titulo': 'Crear nueva promoción'})

def editar_promocion(request, pk):
    promocion_obj = get_object_or_404(Promocion, pk=pk)
    if request.method == 'POST':
        form = PromocionEditarForm(request.POST, instance=promocion_obj)
        if form.is_valid():
            form.save()
            messages.success(request, f"Promoción {promocion_obj.nombre} actualizada.")
            return redirect('listado-promocion')
    else:
        form = PromocionEditarForm(instance=promocion_obj)
    return render(request, 'servicios/editar_promocion.html', {'form': form, 'promocion': promocion_obj})

def eliminar_promocion(request, pk):
    # Nota: Cambié 'id' por 'pk' para mantener consistencia con el urls.py
    promocion_obj = get_object_or_404(Promocion, pk=pk)
    if request.method == 'POST':
        promocion_obj.delete()
        messages.success(request, 'Promoción eliminada.')
        return redirect('listado-promocion')
    return render(request, 'servicios/eliminar_promocion.html', {'promocion': promocion_obj})
    return render(request, 'servicios/listado_calificacion.html', context)


    
   

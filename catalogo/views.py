from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404 # type: ignore
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages # type: ignore
from django.core.mail import send_mail

from usuarios.models import  RolUsuario
from .models import  Promocion
from .forms import PromocionEditarForm, PromocionForm
# Create your views here.

def promocion(request):
    promociones = Promocion.objects.all()
    context = {
        'titulo': 'Promociones',
        'promociones': promociones
    }
    return render(request, 'servicios/promocion.html', context)

def listado_promocion(request):
    promociones = Promocion.objects.all()
    context = {
        'titulo': 'Listado de Promociones',
        'promociones': promociones,
        'total_promociones': promociones.count(),
        'activas': promociones.filter(estado=True).count(),
        'inactivas': promociones.filter(estado=False).count(),
    }
    return render(request, 'servicios/listado-promocion.html', context)



def crear_promocion(request):
    if not (request.user.is_staff or getattr(request.user, 'rol', None) == RolUsuario.ADMIN):
        messages.error(request, "Acceso denegado.")
        return redirect('listado-promocion')

    # 2. Procesamiento cuando se envía el formulario (POST)
    if request.method == 'POST':
        # pasar request.FILES para procesar la imagen
        form = PromocionForm(request.POST, request.FILES)
        
        if form.is_valid():
            nueva_promo = form.save()  # Guarda los datos e imagen en la BD
            messages.success(request, "Promoción creada exitosamente.")
            return redirect('listado-promocion')
        else:
            messages.error(request, "Error al crear la promoción. Por favor revisa los campos.")
    
    
    else:
        form = PromocionForm()
    
    # 4. Renderizado del template
    return render(request, 'servicios/agregar_promocion.html', {
        'form': form,
        'titulo': 'Crear Nueva Promoción'
    })

@login_required
def editar_promocion(request, pk):
    if not (request.user.is_staff or getattr(request.user, 'rol', None) == RolUsuario.ADMIN):
        messages.error(request, "Acceso denegado.")
        return redirect('listado-promocion')

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

@login_required
def eliminar_promocion(request, pk):
    if not (request.user.is_staff or getattr(request.user, 'rol', None) == RolUsuario.ADMIN):
        messages.error(request, "Acceso denegado.")
        return redirect('listado-promocion')

    promocion = get_object_or_404(Promocion, pk=pk)
    if request.method == 'POST':
        promocion.delete()
        messages.success(request, 'Promoción eliminada.')
        return redirect('listado-promocion')
    return render(request, 'servicios/eliminar_promocion.html', {'promocion': promocion})

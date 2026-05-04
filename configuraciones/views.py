from django.shortcuts import render, redirect # type: ignore
from django.contrib import messages
from .models import Carrusel
from .forms import CarruselForm

def carrusel_view(request):
    carruseles = Carrusel.objects.all()

    context = {
        'carruseles': carruseles
    }
    return render(request, 'carrusel.html', context)

def crear_carrusel(request):
    if request.method == 'POST':
        form = CarruselForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Imagen de carrusel creada exitosamente.')
            return redirect('carrusel')
    else:
        form = CarruselForm()
    
    return render(request, 'crear_carrusel.html', {'form': form})

from django.shortcuts import render # type: ignore

# Create your views here.
from .models import Carrusel

def carrusel_view(request):
    carruseles = Carrusel.objects.filter(estado=True)

    context = {
        'carruseles': carruseles
    }
    return render(request, 'carrusel.html', context)




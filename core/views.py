from multiprocessing import context
from django.contrib import messages  # type: ignore


from django.shortcuts import render,redirect, get_object_or_404 # type: ignore

import servicios
from servicios.forms import serviciosEditarForm, serviciosForm

def inicio(request):
    nombre = "Santiago"
    context = {
        'nombre': nombre
    }
    return render(request, 'index-clientes.html', context)

def inicio_admin(request):
    nombre = "Santiago"
    context = {
        'nombre': nombre
    }
    return render(request, 'index-admin.html', context)





# Create your views here.

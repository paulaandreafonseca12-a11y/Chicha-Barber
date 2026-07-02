from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CategoriaAyuda, TicketSoporte

def ayuda_home(request):
    # Trae todas las categorías con sus respectivos artículos indexados
    categorias = CategoriaAyuda.objects.all()
    return render(request, 'ayuda_home.html',)


@login_required
def crear_ticket(request):
    if request.method == 'POST':
        asunto = request.POST.get('asunto')
        descripcion = request.POST.get('descripcion')
        categoria_id = request.POST.get('categoria')
        
        categoria = CategoriaAyuda.objects.get(id=categoria_id) if categoria_id else None
        
        # Guardar el ticket asociado al usuario logueado
        TicketSoporte.objects.create(
            usuario=request.user,
            categoria=categoria,
            asunto=asunto,
            descripcion=descripcion
        )
        # CORREGIDO: Redirección usando el namespace de la app soporte
        return redirect('ayuda_home') 
        
    categorias = CategoriaAyuda.objects.all()
    return render(request, 'crear_ticket.html', {'categorias': categorias})
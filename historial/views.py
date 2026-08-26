from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from .models import Bitacora, HistorialStock


# ==========================================================
# 📜 BITÁCORA DE ACTIVIDAD
# ==========================================================

@login_required
def lista_bitacora(request):
    bitacoras = (
        Bitacora.objects
        .select_related('codigo_usuario')
        .all()
        .order_by('-fecha')
    )

    bitacora_total = bitacoras.count()
    bitacora_entradas = bitacoras.filter(
        Q(accion__icontains='entrada') | Q(descripcion__icontains='entrada')
    ).count()
    bitacora_salidas = bitacoras.filter(
        Q(accion__icontains='salida') | Q(descripcion__icontains='salida')
    ).count()

    context = {
        'titulo': 'Bitácora de Actividades',
        'bitacoras': bitacoras,
        'bitacora_total': bitacora_total,
        'bitacora_entradas': bitacora_entradas,
        'bitacora_salidas': bitacora_salidas,
    }

    return render(
        request,
        'historial/bitacora/bitacora.html',
        context
    )


@login_required
def editar_bitacora(request, pk):
    get_object_or_404(Bitacora, pk=pk)

    messages.info(
        request,
        "La edición manual de la bitácora está deshabilitada. Los eventos se registran de forma automática."
    )

    return redirect('lista_bitacora')

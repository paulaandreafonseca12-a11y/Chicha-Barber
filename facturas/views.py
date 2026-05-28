from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Factura


# =========================
# FACTURAS CLIENTE
# =========================
@login_required
def facturas(request):
    facturas = (
        request.user.facturas
        .prefetch_related(
            'detalles__producto',
            'detalles__reserva__servicio'
        )
        .select_related('cliente')
        .order_by('-fecha_emision')
    )

    return render(request, 'facturas/factura.html', {
        'facturas': facturas
    })


# =========================
# FACTURAS ADMIN
# =========================
def factura_adm(request):

    facturas = (
        Factura.objects
        .all()
        .select_related('cliente')
        .prefetch_related(
            'detalles__producto',
            'detalles__reserva__servicio'
        )
        .order_by('-fecha_emision')
    )

    return render(request, 'facturas/factura-adm.html', {
        'facturas': facturas
        
    })


# =========================
# CREAR FACTURA
# =========================
def crear_factura(request):

    return render(request, 'facturas/crear-factura.html')
    titulo = "Crear nueva factura"


# =========================
# DETALLE FACTURA
# =========================
def detalle_factura(request, id):

    factura = get_object_or_404(
        Factura.objects.prefetch_related(
            'detalles__producto',
            'detalles__reserva__servicio'
        ).select_related('cliente'),
        id=id
    )

    return render(request, 'facturas/detalle-factura.html', {
        'factura': factura,
        'titulo': "Detalle de la factura",
        
    })

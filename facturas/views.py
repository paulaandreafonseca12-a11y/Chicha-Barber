import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages

from .models import Factura 

# --- CORRECCIÓN DE IMPORTACIONES ---
# Si usas el User nativo de Django o extendido en 'usuarios':
from django.contrib.auth import get_user_model
Cliente = get_user_model() # Esto traerá automáticamente el modelo de usuarios/clientes que tengas configurado

# Asegúrate de que estos tres sí se llamen así en sus respectivas apps:
from productos.models import Producto     
from servicios.models import Servicios     
from servicios.models import Promocion


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
    return render(request, 'facturas/factura.html', {'facturas': facturas})


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
        'facturas': facturas,
        'title': "Gestión de Facturas"
    })


# =========================
# CREAR FACTURA
# =========================
def crear_factura(request):
    if request.method == 'POST':
        # Aquí procesas el envío del formulario tradicional
        cliente_id = request.POST.get('cliente')
        metodo_pago = request.POST.get('metodo_pago')
        total_pagado = request.POST.get('total_pagado')
        estado = request.POST.get('estado')
        observaciones = request.POST.get('observaciones')
        
        # Opcionales según tu lógica de negocio
        servicio_id = request.POST.get('servicio')
        producto_id = request.POST.get('producto')
        promocion_id = request.POST.get('promocion')

        try:
            # Creación del registro de la factura
            factura = Factura.objects.create(
                cliente_id=cliente_id,
                metodo_pago=metodo_pago,
                total_pagado=total_pagado,
                estado=estado,
                # Agrega aquí tus campos adicionales de observaciones, etc.
            )
            
            # NOTA: Si manejas una tabla intermedia de detalles, aquí asocias 
            # el producto_id o servicio_id creados al objeto 'factura'.

            messages.success(request, "Factura creada exitosamente.")
            return redirect('factura_adm')
        except Exception as e:
            messages.error(request, f"Error al crear la factura: {e}")

    # CONSULTAS A LA BASE DE DATOS PARA LLENAR LOS SELECTS
    # Modifica 'User' o 'Cliente.objects' según cómo se llame tu modelo de usuarios de confianza
    clientes = Cliente.objects.all() 
    servicios = Servicios.objects.all()
    productos = Producto.objects.all()
    promociones = Promocion.objects.all()

    return render(request, 'facturas/crear-factura.html', {
        'titulo': "Crear nueva factura",
        'clientes': clientes,
        'servicios': servicios,
        'productos': productos,
        'promociones': promociones
    })


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
        'titulo': "Detaille de la factura",
    })


# =========================
# IMPRIMIR FACTURA
# =========================
def imprimir_factura(request, id):
    factura = get_object_or_404(
        Factura.objects.prefetch_related(
            'detalles__producto',
            'detalles__reserva__servicio'
        ).select_related('cliente'),
        id=id
    )
    return render(request, 'facturas/imprimir-factura.html', {'factura': factura})


# =========================
# ACTUALIZAR FACTURA AJAX
# =========================
@login_required
@csrf_protect
def actualizar_factura_adm(request, id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            factura = get_object_or_404(Factura, id=id)
            
            if 'estado' in data: factura.estado = data['estado']
            if 'metodo_pago' in data: factura.metodo_pago = data['metodo_pago']
                
            factura.save()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'invalid method'}, status=405)
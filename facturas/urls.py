from django.urls import path
from . import views

urlpatterns = [

    # CLIENTE
    path(
        '',
        views.facturas,
        name='facturas'
    ),

    # ADMIN
    path(
        'admin/',
        views.factura_adm,
        name='factura_adm'
    ),

    # CREAR
    path(
        'crear/',
        views.crear_factura,
        name='crear-factura'
    ),

    # DETALLE
    path(
        'detalle/<int:id>/',
        views.detalle_factura,
        name='detalle_factura'
    ),

    # ACTUALIZAR (AJAX)
    path(
        'actualizar-factura-adm/<int:id>/',
        views.actualizar_factura_adm,
        name='actualizar_factura_adm'
    ),

    # IMPRIMIR
    path(
        'factura/imprimir/<int:id>/',
        views.imprimir_factura,
        name='imprimir_factura'
    ),

]

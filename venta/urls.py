from django.urls import path
from . import views

urlpatterns = [
    # =========================
    # 🛒 CLIENTE / CHECKOUT
    # =========================
    path('carrito/', views.carrito, name='carrito'),
    path('agregar-carrito/', views.agregar_carrito, name='agregar_carrito'),
    path('pago/', views.pago, name='pago'),
    path('procesar-pago/', views.procesar_pago_cliente, name='procesar_pago_cliente'),
    path('procesar_pago_cliente/', views.procesar_pago_cliente, name='procesar_venta'),

    # =========================
    # 📊 VENTAS ADMIN
    # =========================
    path('historial/', views.historial_ventas, name='historial_ventas'),
    path('historial/registrar/', views.registrar_venta, name='registrar_venta'),
    path('historial/<int:pk>/', views.detalle_venta, name='detalle_venta'),
    path('historial/eliminar/<int:pk>/', views.eliminar_venta, name='eliminar_venta'),

    # =========================
    # 🏦 DATOS BANCARIOS
    # =========================
    path('configuracion/datos-banco/', views.ver_datos_banco, name='ver_datos_banco'),
    path('configuracion/datos-banco/editar/', views.editar_datos_banco, name='editar_datos_banco'),
]

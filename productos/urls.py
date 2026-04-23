from django.urls import path
from . import views

urlpatterns = [

    # =========================
    # 🟢 CLIENTE
    # =========================
    path('', views.productos_galeria, name='productos_galeria'),
    path('carrito/', views.carrito, name='carrito'),
    path('pago/', views.pago, name='pago'),
    path('procesar_compra/', views.procesar_pago_cliente, name='procesar_pago_cliente'),

    # =========================
    # 🔵 ADMIN PRODUCTOS
    # =========================
    path('gestion/', views.lista_productos_admin, name='lista_productos_admin'),
    path('producto/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('producto/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),

    # =========================
    # 🔥 STOCK
    # =========================
    path('stock/', views.lista_stock, name='lista_stock'),  # 👈 INVENTARIO (tabla)
    path('stock/editar/<int:pk>/', views.editar_stock, name='editar_stock'),

    # =========================
    # 🟡 COMPRAS
    # =========================
    path('registrar-compra/', views.registrar_compra, name='registrar_compra'),
    path('historial/', views.historial_compras, name='historial_compras'),
    path('historial/<int:pk>/', views.detalle_compra, name='detalle_compra'),
    path('historial/eliminar/<int:pk>/', views.eliminar_compra, name='eliminar_compra'),

]
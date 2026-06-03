from django.urls import path
from . import views

urlpatterns = [

    # =========================
    # 🟢 CLIENTE
    # =========================
    path('', views.productos_galeria, name='productos_galeria'),
    path('carrito/', views.carrito, name='carrito'),
    path('pago/', views.pago, name='pago'),
    path('procesar_pago_cliente/', views.procesar_pago_cliente, name='procesar_compra'),
    # =========================
    # 🔵 ADMIN PRODUCTOS
    # =========================
    path('gestion/', views.lista_productos_admin, name='lista_productos_admin'),
    path('producto/crear/', views.crear_producto, name='crear_producto'),  # 👈 NUEVO
    path('producto/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('producto/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),
    path('configuracion/datos-banco/', views.ver_datos_banco, name='ver_datos_banco'), # Para ver los datos
    path('configuracion/datos-banco/editar/', views.editar_datos_banco, name='editar_datos_banco'), # Para editar los datos

    # =========================
    # 🔥 STOCK
    # =========================
    path('stock/', views.lista_stock, name='lista_stock'),
    path('stock/editar/<int:pk>/', views.editar_stock, name='editar_stock'),

    # =========================
    # 🟡 COMPRAS
    # =========================
    path('registrar-compra/', views.registrar_compra, name='registrar_compra'),
    path('historial/registrar/', views.registrar_compra, name='registrar_compra'),  # ← nueva
    path('historial/', views.historial_compras, name='historial_compras'),
    path('historial/<int:pk>/', views.detalle_compra, name='detalle_compra'),
    path('historial/eliminar/<int:pk>/', views.eliminar_compra, name='eliminar_compra'),
]
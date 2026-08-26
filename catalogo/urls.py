from django.urls import path
from . import views

urlpatterns = [
    # =========================
    # 🟢 CLIENTE / PÚBLICO
    # =========================
    path('', views.productos_galeria, name='productos_galeria'),

    # =========================
    # 🔵 ADMIN PRODUCTOS
    # =========================
    path('gestion/', views.lista_productos_admin, name='lista_productos_admin'),
    path('producto/crear/', views.crear_producto, name='crear_producto'),
    path('producto/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('producto/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),

    # =========================
    # 🟣 CATEGORÍAS
    # =========================
    path('categorias/', views.lista_categorias, name='lista_categorias'),
    path('categoria/crear/', views.crear_categoria, name='crear_categoria'),
    path('categoria/editar/<int:id>/', views.editar_categoria, name='editar_categoria'),
    path('categoria/eliminar/<int:id>/', views.eliminar_categoria, name='eliminar_categoria'),

    # =========================
    # 🟣 PROVEEDORES
    # =========================
    path('proveedores/', views.lista_proveedores, name='lista_proveedores'),
    path('proveedor/crear/', views.crear_proveedor, name='crear_proveedor'),
    path('proveedor/editar/<int:id>/', views.editar_proveedor, name='editar_proveedor'),
    path('proveedor/eliminar/<int:id>/', views.eliminar_proveedor, name='eliminar_proveedor'),

    # =========================
    # 🏷️ MARCAS
    # =========================
    path('marcas/', views.lista_marcas, name='lista_marcas'),
    path('marca/crear/', views.crear_marca, name='crear_marca'),
    path('marcas/editar/<int:id>/', views.editar_marca, name='editar_marca'),
    path('marcas/eliminar/<int:id>/', views.eliminar_marca, name='eliminar_marca'),

    # =========================
    # 📦 EXISTENCIAS / STOCK
    # =========================
    path('existencias/', views.lista_existencias, name='lista_existencias'),
    path('existencias/editar/<int:pk>/', views.editar_existencias, name='editar_existencias'),

    # =========================
    # 🔄 MOVIMIENTOS DE EXISTENCIAS
    # =========================
    path('movimientos-existencias/', views.lista_movimientos_existencias, name='lista_movimientos_existencias'),
    path('movimientos-existencias/registrar/', views.registrar_movimiento_existencias, name='registrar_movimiento_existencias'),
    path('movimientos-existencias/eliminar/<int:pk>/', views.eliminar_movimiento_existencias, name='eliminar_movimiento_existencias'),
]




path('promocion/', views.promocion, name='promocion'),
    
path('crear-promocion/', views.crear_promocion, name='crear_promocion'),

path('promocion/listado/', views.listado_promocion, name='listado-promocion'),
path('promocion/editar/<int:pk>/', views.editar_promocion, name='editar-promocion'),
path('promocion/eliminar/<int:pk>/', views.eliminar_promocion, name='eliminar-promocion'),

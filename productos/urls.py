"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
https://docs.djangoproject.com/en/6.0/topics/http/urls/

Examples:

Function views
1. Add an import: from my_app import views
2. Add a URL to urlpatterns: path('', views.home, name='home')

Class-based views
1. Add an import: from other_app.views import Home
2. Add a URL to urlpatterns: path('', Home.as_view(), name='home')

Including another URLconf
1. Import the include() function: from django.urls import include, path
2. Add a URL to urlpatterns: path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views


urlpatterns = [
    # Rutas Cliente
    path('', views.productos_galeria, name='productos_galeria'),
    path('carrito/', views.carrito, name='carrito'),
    path('pago/', views.pago, name='pago'),
    path('procesar_compra/', views.procesar_pago_cliente, name='procesar_pago_cliente'),

    # Rutas Admin
    path('gestion/', views.lista_productos_admin, name='lista_productos_admin'),
    path('registrar-compra/', views.registrar_compra, name='registrar_compra'),
    path('crear_producto/', views.crear_producto, name='crear_producto'),
    path('historial/', views.historial_compras, name='historial_compras'),
    path('historial/<int:pk>/', views.detalle_compra, name='detalle_compra'),       # ← nuevo
    path('producto/editar/<int:pk>/', views.editar_producto, name='editar_producto'), # ← nuevo
  path('historial/eliminar/<int:pk>/', views.eliminar_compra, name='eliminar_compra'),
    path('producto/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'), # ← nuevo
]
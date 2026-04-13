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

from django.contrib import admin
from django.urls import path, include
from . import views


urlpatterns = [
    path ('productos/', views.productos, name='productos'),
    path ('productos/carrito/', views.carrito, name='carrito'),
    path ('productos/pago/', views.pago, name='pago'),
    path('procesar_compra/', views.procesar_compra, name='procesar_compra'),
    path('admin/productos/', views.lista_productos, name='lista_productos'),
    path('admin/productos/crear/', views.crear_producto, name='crear_producto'),

   # path('crear-producto/', views.crear_producto, name='crear_producto'),
]